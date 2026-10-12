import pandas as pd
from experta import KnowledgeEngine, Fact, Rule, MATCH, P
import os

# =============================
# Load course data from CSVs with safe encoding
# =============================
def safe_read_csv(path):
    try:
        df = pd.read_csv(path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding='ISO-8859-1')
    df.columns = df.columns.str.strip().str.lower()
    df.fillna('', inplace=True)
    df['source file'] = os.path.basename(path).lower()
    return df

# ✅ Load files
core_courses = safe_read_csv("kbs(in) (2).csv")
electives_courses = pd.concat([
    safe_read_csv("kbs(Elective Course (1)) (1).csv"),
    safe_read_csv("kbs(Elective Course (5)).csv"),
    safe_read_csv("kbs(Elective Course (6)) (1).csv"),
    safe_read_csv("kbs(Elective course 2) (1).csv"),
    safe_read_csv("kbs(Elective Course 3) (2).csv"),
    safe_read_csv("kbs(Elective couser 4) (1).csv")
], ignore_index=True)
university_courses = safe_read_csv("kbs(University Requirement) (1).csv")

print("\n✅ All course files loaded successfully!")

class StudentInfo(Fact):
    pass

class CourseAdviser(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.recommendations = []
        self.exclusions = []
        self.total_credits = 0
        self.max_credits = 0

    @Rule(StudentInfo(CGPA=P(lambda x: x < 2.0)))
    def cgpa_low(self):
        self.max_credits = 12

    @Rule(StudentInfo(CGPA=P(lambda x: 2.0 <= x < 3.0)))
    def cgpa_mid(self):
        self.max_credits = 18

    @Rule(StudentInfo(CGPA=P(lambda x: x >= 3.0)))
    def cgpa_high(self):
        self.max_credits = 22

    @Rule(StudentInfo(SemesterPlan=MATCH.plan, CurrentSemester=MATCH.sem, Passed=MATCH.passed, Failed=MATCH.failed))
    def recommend_courses(self, plan, sem, passed, failed):
        # 🔁 PRIORITIZE failed courses
        for code in failed:
            course_row = core_courses[core_courses['course code'].str.strip().str.upper() == code]
            if course_row.empty:
                continue
            row = course_row.iloc[0]
            credits = int(row['credit hours']) if str(row['credit hours']).isdigit() else 0
            prereq_col = [col for col in row.index if 'pre' in col and 'requ' in col.lower()]
            prereqs = str(row[prereq_col[0]] if prereq_col else '').strip().split(',')
            prereqs = [p.strip().upper() for p in prereqs if p.strip()]
            unmet = [p for p in prereqs if p not in passed]
            if unmet:
                self.exclusions.append({"Course Code": code, "Reason": f"Unmet prerequisites (failed): {', '.join(unmet)}"})
                continue
            if code not in [r['Course Code'] for r in self.recommendations] and self.total_credits + credits <= self.max_credits:
                self.recommendations.append({"Course Code": code, "Credit Hours": credits, "Reason": "Priority retake of failed course"})
                self.total_credits += credits

        # 🔁 Courses from semester plan
        plan_df = core_courses[core_courses['semester'].astype(str) == str(plan)]
        plan_df = plan_df[plan_df['semester offered'].str.lower().isin([sem.lower(), 'both'])]
        for _, row in plan_df.iterrows():
            code = row['course code'].strip().upper()
            credits = int(row['credit hours']) if str(row['credit hours']).isdigit() else 0
            prereq_col = [col for col in row.index if 'pre' in col and 'requ' in col.lower()]
            prereqs = str(row[prereq_col[0]] if prereq_col else '').strip().split(',')
            prereqs = [p.strip().upper() for p in prereqs if p.strip()]
            if code.startswith("UC") or code in passed or code in [r['Course Code'] for r in self.recommendations]:
                continue
            unmet = [p for p in prereqs if p not in passed]
            if unmet:
                self.exclusions.append({"Course Code": code, "Reason": f"Unmet prerequisites: {', '.join(unmet)}"})
                continue
            if self.total_credits + credits <= self.max_credits:
                self.recommendations.append({"Course Code": code, "Credit Hours": credits, "Reason": "Planned course recommendation"})
                self.total_credits += credits

        # 🔁 Future failed courses
        future_df = core_courses[core_courses['semester'].astype(str) > str(plan)]
        for _, row in future_df.iterrows():
            code = row['course code'].strip().upper()
            credits = int(row['credit hours']) if str(row['credit hours']).isdigit() else 0
            prereq_col = [col for col in row.index if 'pre' in col and 'requ' in col.lower()]
            prereqs = str(row[prereq_col[0]] if prereq_col else '').strip().split(',')
            prereqs = [p.strip().upper() for p in prereqs if p.strip()]
            if code in failed and code not in [r['Course Code'] for r in self.recommendations]:
                unmet = [p for p in prereqs if p not in passed]
                if unmet:
                    continue
                if self.total_credits + credits <= self.max_credits:
                    self.recommendations.append({"Course Code": code, "Credit Hours": credits, "Reason": "Retake failed course (future semester)"})
                    self.total_credits += credits

        # 📘 Electives and University Requirements from actual core data
        elective_df = core_courses[(core_courses['semester'].astype(str) == str(plan)) & core_courses['course code'].str.startswith(('E', 'U'), na=False)]
        for _, row in elective_df.iterrows():
            code = row['course code'].strip().upper()
            reason = row['course name'].strip()
            group_num = ''.join(filter(str.isdigit, code))
            if code.startswith("E"):
                elective_mask = f"elective course ({group_num})"
                group = electives_courses[electives_courses['source file'].str.contains(elective_mask, case=False, na=False)]
                if not group.empty:
                    print(f"\n📗 Elective {group_num} Courses:")
                    for _, r in group.iterrows():
                        print(f"- {r['course code']}: {r['course name']}")
                    selected = input(f"Enter the course code to take from Elective {group_num}: ").strip().upper()
                    match = group[group['course code'] == selected]
                    if not match.empty:
                        crs = match.iloc[0]
                        credits = 3
                        if self.total_credits + credits <= self.max_credits:
                            self.recommendations.append({"Course Code": crs['course code'], "Credit Hours": credits, "Reason": f"Elective {group_num}"})
                            self.total_credits += credits
                            print(f"✅ Added {crs['course code']} to your recommendations.")
            elif code.startswith("UE"):
                group = electives_courses[electives_courses['source file'].str.contains("elective university", case=False, na=False)]
                if not group.empty:
                    print(f"\n📙 University Elective Courses:")
                    for _, r in group.iterrows():
                        print(f"- {r['course code']}: {r['course name']}")
                    selected = input("Enter the course code to take from University Electives: ").strip().upper()
                    match = group[group['course code'] == selected]
                    if not match.empty:
                        crs = match.iloc[0]
                        credits = 3
                        if self.total_credits + credits <= self.max_credits:
                            self.recommendations.append({"Course Code": crs['course code'], "Credit Hours": credits, "Reason": "University Elective"})
                            self.total_credits += credits
                            print(f"✅ Added {crs['course code']} to your recommendations.")

# ==== End of Rules Section ====

semester_plan = input("Enter your Semester Plan (e.g. 1 for first semester): ")
current_semester = input("Enter your current Semester (Fall or Spring): ").strip()

if semester_plan == "1":
    print("\nSince it's your first semester, CGPA and passed/failed courses are not required.")
    passed_courses = []
    failed_courses = []
    cgpa = 3.0
    max_credits_override = 20
else:
    cgpa = float(input("Enter your CGPA: "))
    passed_courses = input("Enter passed courses (by course code) separated by commas: ").split(',')
    passed_courses = [c.strip().upper() for c in passed_courses if c.strip()]
    failed_courses = input("Enter failed courses (by course code) separated by commas: ").split(',')
    failed_courses = [c.strip().upper() for c in failed_courses if c.strip()]
    max_credits_override = None

print("\n✅ Summary:")
print("Passed:", ", ".join(passed_courses) if passed_courses else "None")
print("Failed:", ", ".join(failed_courses) if failed_courses else "None")

engine = CourseAdviser()
engine.reset()
engine.declare(StudentInfo(
    CGPA=cgpa,
    SemesterPlan=semester_plan,
    CurrentSemester=current_semester,
    Passed=passed_courses,
    Failed=failed_courses
))
engine.run()

if max_credits_override:
    engine.max_credits = max_credits_override

uc_required = core_courses[
    (core_courses['semester'].astype(str) == semester_plan) &
    (core_courses['course code'].str.upper().str.startswith("UC"))
]

selected_codes = []
if not uc_required.empty:
    print("\n📘 University Requirement Courses:")
    for _, row in university_courses.iterrows():
        print(f"- {row['course code']}: {row['course name']}")
    selected_codes = input("\nEnter the course code(s) you want to take from University Requirement (comma-separated): ").strip().upper().split(',')
    for selected_code in selected_codes:
        selected_code = selected_code.strip()
        selected_row = university_courses[university_courses['course code'] == selected_code]
        if not selected_row.empty:
            selected_course = selected_row.iloc[0]
            if selected_course['course code'] not in [r['Course Code'] for r in engine.recommendations]:
                engine.recommendations.append({
                    "Course Code": selected_course['course code'],
                    "Credit Hours": 2,
                    "Reason": "University Requirement"
                })
                engine.total_credits += 2
                print(f"✅ Added {selected_course['course code']} to your recommendations.")

# ✅ Remove UC courses from the semester plan after manual selection
core_courses = core_courses[~(
    (core_courses['semester'].astype(str) == semester_plan) &
    (core_courses['course code'].str.upper().isin([code.strip().upper() for code in selected_codes]))
)]

# Show Elective Courses based on semester
elective_mapping = {
    "2": [1],
    
    "6": [3],
    "7": [3, 4],
    "9": [3, 4]
}
if semester_plan in elective_mapping:
    for elective_num in elective_mapping[semester_plan]:
        elective_file_mask = f"elective course ({elective_num})"
        electives_group = electives_courses[electives_courses['source file'].str.contains(elective_file_mask, case=False, na=False)]
        if not electives_group.empty:
            print(f"\n📗 Elective {elective_num} Courses:")
            for _, row in electives_group.iterrows():
                print(f"- {row['course code']}: {row['course name']}")
            selected_elective = input(f"Enter the course code to take from Elective {elective_num}: ").strip().upper()
            elective_row = electives_group[electives_group['course code'] == selected_elective]
            if not elective_row.empty:
                elective_course = elective_row.iloc[0]
                elective_credits = 3
                if elective_course['course code'].strip().upper() not in [r['Course Code'] for r in engine.recommendations]:
                    if engine.total_credits + elective_credits <= engine.max_credits:
                        engine.recommendations.append({
                            "Course Code": elective_course['course code'],
                            "Credit Hours": elective_credits,
                            "Reason": f"Elective {elective_num}"
                        })
                        engine.total_credits += elective_credits
                        print(f"✅ Added {elective_course['course code']} to your recommendations.")
                    else:
                        print("❌ Cannot add elective course. It exceeds your max credit hours.")

print("\n📋 Final Recommended Courses:")
if engine.recommendations:
    for rec in engine.recommendations:
        print(f"- {rec['Course Code']} ({rec['Credit Hours']} credits): {rec['Reason']}")
else:
    print("No courses could be recommended based on the current inputs.")

print("\n🚫 Excluded Courses:")
if engine.exclusions:
    for exc in engine.exclusions:
        print(f"- {exc['Course Code']}: {exc['Reason']}")
else:
    print("No courses were excluded.")

print(f"\n🎯 Total Credit Hours: {engine.total_credits} / {engine.max_credits}")