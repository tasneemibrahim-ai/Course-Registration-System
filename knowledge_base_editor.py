import streamlit as st
import pandas as pd
import os

# =============================
# 1. Load all CSV course files from the current directory
# =============================
def load_course_data():
    directory = "./"
    all_courses = pd.DataFrame()

    standard_columns = [
        "semester", "course code", "course name", "description",
        "pre requsit", "co-requsit", "credit hours", "semester offered"
    ]

    for file in os.listdir(directory):
        if file.endswith(".csv"):
            file_path = os.path.join(directory, file)
            if os.path.getsize(file_path) == 0:
                continue

            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='ISO-8859-1')

            if df.empty:
                continue

            df.columns = df.columns.str.strip().str.lower()
            if "course name.1" in df.columns and "course name" in df.columns:
                if df["course name"].str.match(r'[A-Z]{2,}\d{3,}').all():
                    df["course code"] = df["course name"]
                    df["course name"] = df["course name.1"]

            df = df.loc[:, ~df.columns.duplicated()]
            df.columns = [col.replace("cousre name", "course name") for col in df.columns]

            for col in standard_columns:
                if col not in df.columns:
                    df[col] = ""

            df["source file"] = file
            all_courses = pd.concat([all_courses, df[standard_columns + ["source file"]]], ignore_index=True)

    return all_courses

def save_courses(df, filename="updated_courses.csv"):
    df.to_csv(filename, index=False)

# =============================
# 3. Streamlit App
# =============================
def main():
    st.set_page_config(page_title="Knowledge Base Editor", layout="wide")
    st.title("🧠 Knowledge Base Editor for Courses")

    courses_df = load_course_data()

    if "source file" in courses_df.columns:
        st.subheader("📘 Main/Core Courses")
        main_courses = courses_df[courses_df["source file"].str.contains("in", case=False)]
        st.dataframe(main_courses)

        st.subheader("📗 Elective Courses")
        elective_courses = courses_df[courses_df["source file"].str.contains("elective", case=False)]
        st.dataframe(elective_courses)

        st.subheader("📙 University Requirements")
        req_courses = courses_df[courses_df["source file"].str.contains("requirement", case=False)]
        st.dataframe(req_courses)
    else:
        st.error("⚠️ No valid data loaded. Please check your CSV files.")

    st.subheader("➕ Add New Course")
    with st.form("add_form"):
        new_code = st.text_input("Course Code")
        new_name = st.text_input("Course Name")
        new_description = st.text_area("Description")
        new_pre = st.text_input("Pre-requisite (optional)")
        new_co = st.text_input("Co-requisite (optional)")
        new_credits = st.number_input("Credit Hours", min_value=1, max_value=10, step=1)
        new_semester = st.text_input("Semester Offered")
        new_sem_num = st.text_input("Semester (e.g., 1, 2)")
        course_type = st.selectbox("Course Type", [
            "Core", "University Requirement", "Elective University",
            "Elective 1", "Elective 2", "Elective 3",
            "Elective 4", "Elective 5", "Elective 6"
        ])
        add_button = st.form_submit_button("Add Course")

        if add_button:
            if new_code in courses_df["course code"].astype(str).values:
                st.warning("⚠️ This course code already exists.")
            elif new_pre and new_pre not in courses_df["course code"].astype(str).values:
                st.error("❌ Pre-requisite not found.")
            elif new_co and new_co not in courses_df["course code"].astype(str).values:
                st.error("❌ Co-requisite not found.")
            else:
                file_name_map = {
                    "Core": "kbs(in).csv",
                    "University Requirement": "kbs(University Requirement).csv",
                    "Elective University": "kbs(Elective University).csv",
                    "Elective 1": "kbs(Elective Course (1)).csv",
                    "Elective 2": "kbs(Elective course 2).csv",
                    "Elective 3": "kbs(Elective Course 3).csv",
                    "Elective 4": "kbs(Elective couser 4).csv",
                    "Elective 5": "kbs(Elective Course (5)).csv",
                    "Elective 6": "kbs(Elective Course (6)).csv"
                }
                selected_file = file_name_map[course_type]
                new_row = {
                    "semester": new_sem_num,
                    "course code": new_code,
                    "course name": new_name,
                    "description": new_description,
                    "pre requsit": new_pre,
                    "co-requsit": new_co,
                    "credit hours": new_credits,
                    "semester offered": new_semester,
                    "source file": selected_file
                }

                if os.path.exists(selected_file):
                    existing_df = pd.read_csv(selected_file)
                    updated_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
                else:
                    updated_df = pd.DataFrame([new_row])
                updated_df.to_csv(selected_file, index=False)
                courses_df = pd.concat([courses_df, pd.DataFrame([new_row])], ignore_index=True)
                save_courses(courses_df)
                st.success("✅ Course added successfully.")

    # EDIT Course
    st.subheader("✏️ Edit Existing Course")
    if "course code" in courses_df.columns:
        course_options = courses_df["course code"].dropna().astype(str).unique()
        if len(course_options) > 0:
            selected_code = st.selectbox("Select course code to edit", course_options)
            if selected_code:
                row = courses_df[courses_df["course code"].astype(str) == selected_code].iloc[0]
                with st.form("edit_form"):
                    edited_name = st.text_input("Course Name", row["course name"])
                    edited_description = st.text_area("Description", row["description"])
                    edited_pre = st.text_input("Pre-requisite", row["pre requsit"])
                    edited_co = st.text_input("Co-requisite", row["co-requsit"])
                    edited_credits = st.number_input(
                        "Credit Hours", min_value=1, max_value=10,
                        value=int(row["credit hours"]) if str(row["credit hours"]).isdigit() else 3
                    )
                    edited_semester = st.text_input("Semester Offered", row["semester offered"])
                    edited_sem_num = st.text_input("Semester", row["semester"])
                    edit_button = st.form_submit_button("Update Course")

                    if edit_button:
                        idx = courses_df[courses_df["course code"].astype(str) == selected_code].index[0]
                        courses_df.at[idx, "course name"] = edited_name
                        courses_df.at[idx, "description"] = edited_description
                        courses_df.at[idx, "pre requsit"] = edited_pre
                        courses_df.at[idx, "co-requsit"] = edited_co
                        courses_df.at[idx, "credit hours"] = edited_credits
                        courses_df.at[idx, "semester offered"] = edited_semester
                        courses_df.at[idx, "semester"] = edited_sem_num
                        save_courses(courses_df)
                        st.success("✅ Course updated.")
        else:
            st.warning("⚠️ No available courses to edit.")
    else:
        st.warning("⚠️ No 'course code' column available.")

    # DELETE Course
    st.subheader("❌ Delete Course")
    if "course code" in courses_df.columns and len(courses_df) > 0:
        delete_options = courses_df["course code"].dropna().astype(str).unique()
        delete_code = st.selectbox("Select course code to delete", delete_options)
        if st.button("Delete Course"):
            courses_df = courses_df[courses_df["course code"].astype(str) != delete_code]
            save_courses(courses_df)
            st.success(f"🗑️ Course '{delete_code}' deleted successfully.")
    else:
        st.warning("⚠️ No courses available to delete.")

if __name__ == "__main__":
    main()