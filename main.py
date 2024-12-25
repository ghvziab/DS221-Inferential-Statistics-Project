import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import os

# Main Grading Application Class
class GradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grading System Application")
        self.root.geometry("500x600")
        
        # Variables
        self.grading_type = tk.StringVar(value="absolute")
        self.file_path = None
        self.data = None

        # GUI Components
        self.create_widgets()

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Grading System", font=("Arial", 16)).pack(pady=10)

        # File Upload
        tk.Button(self.root, text="Upload Grades CSV", command=self.upload_file).pack(pady=5)

        # Grading Type Selection
        tk.Label(self.root, text="Select Grading Type:").pack(pady=5)
        tk.Radiobutton(self.root, text="Absolute Grading", variable=self.grading_type, value="absolute").pack()
        tk.Radiobutton(self.root, text="Relative Grading", variable=self.grading_type, value="relative").pack()

        # Grade Thresholds for Absolute Grading
        tk.Label(self.root, text="Grade Thresholds (Absolute Grading):").pack(pady=10)
        self.thresholds_entry = tk.Entry(self.root)
        self.thresholds_entry.insert(0, "A:90,B:80,C:70,D:60,F:50")
        self.thresholds_entry.pack()

        # Grade Distribution for Relative Grading
        tk.Label(self.root, text="Grade Distribution (Relative Grading):").pack(pady=10)
        self.distribution_entry = tk.Entry(self.root)
        self.distribution_entry.insert(0, "A:20,B:30,C:30,D:15,F:5")
        self.distribution_entry.pack()

        # Process Grades Button
        tk.Button(self.root, text="Process Grades", command=self.process_grades).pack(pady=10)

        # Statistics Button
        tk.Button(self.root, text="Show Statistics", command=self.show_statistics).pack(pady=5)

        # Visualization Button
        tk.Button(self.root, text="Visualize Data", command=self.visualize_data).pack(pady=5)

        # Save Report Button
        tk.Button(self.root, text="Save Report", command=self.save_report).pack(pady=10)

    def upload_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.file_path:
            try:
                self.data = pd.read_csv(self.file_path)
                messagebox.showinfo("Success", "File uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")

    def process_grades(self):
        if self.data is None:
            messagebox.showerror("Error", "Please upload a valid grades file.")
            return

        grading_type = self.grading_type.get()
        if grading_type == "absolute":
            self.apply_absolute_grading()
        elif grading_type == "relative":
            self.apply_relative_grading()

    def apply_absolute_grading(self):
        try:
            thresholds = self.parse_thresholds(self.thresholds_entry.get())
            self.data["Grade"] = self.data["exam1"].apply(lambda x: self.get_absolute_grade(x, thresholds))
            messagebox.showinfo("Success", "Absolute grading applied successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error in absolute grading: {e}")

    def apply_relative_grading(self):
        try:
            distribution = self.parse_distribution(self.distribution_entry.get())
            self.data = self.calculate_relative_grades(self.data, distribution)
            messagebox.showinfo("Success", "Relative grading applied successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error in relative grading: {e}")

    def show_statistics(self):
        if self.data is None:
            messagebox.showerror("Error", "No data to show statistics for.")
            return

        stats = self.data["exam1"].describe()
        messagebox.showinfo("Statistics", stats.to_string())

    def visualize_data(self):
        if self.data is None:
            messagebox.showerror("Error", "No data to visualize.")
            return

    # Plot the original scores histogram
        plt.hist(self.data["exam1"], bins=10, alpha=0.7, color="skyblue", label="Original")

    # Fit and plot the normal distribution curve
        mean = self.data["exam1"].mean()
        std = self.data["exam1"].std()
        x = np.linspace(self.data["exam1"].min(), self.data["exam1"].max(), 100)
        y = norm.pdf(x, mean, std) * len(self.data["exam1"]) * (self.data["exam1"].max() - self.data["exam1"].min()) / 10
        plt.plot(x, y, color="red", label="Normal Distribution")

    # Add labels and legend
        plt.legend()
        plt.title("Grade Distribution with Normal Curve")
        plt.xlabel("Scores")
        plt.ylabel("Frequency")
        plt.show()


    def save_report(self):
        if self.data is None:
            messagebox.showerror("Error", "No data to save.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if save_path:
            self.data.to_csv(save_path, index=False)
            messagebox.showinfo("Success", "Report saved successfully!")

    def parse_thresholds(self, thresholds_str):
        thresholds = {}
        for pair in thresholds_str.split(","):
            grade, value = pair.split(":")
            thresholds[grade] = float(value)
        return thresholds

    def get_absolute_grade(self, score, thresholds):
        for grade, threshold in thresholds.items():
            if score >= threshold:
                return grade
        return "F"

    def parse_distribution(self, distribution_str):
        distribution = {}
        for pair in distribution_str.split(","):
            grade, value = pair.split(":")
            distribution[grade] = float(value)
        return distribution

    def calculate_relative_grades(self, data, distribution):
        sorted_scores = data["exam1"].sort_values()
        total_students = len(sorted_scores)

        cumulative_percentages = np.cumsum([distribution[grade] for grade in distribution])
        cumulative_percentages /= cumulative_percentages[-1]

        grades = list(distribution.keys())
        grade_thresholds = [int(cumulative_percentages[i] * total_students) for i in range(len(grades))]

        data["Grade"] = ""
        start_idx = 0
        for i, grade in enumerate(grades):
            end_idx = grade_thresholds[i]
            data.loc[sorted_scores.index[start_idx:end_idx], "Grade"] = grade
            start_idx = end_idx

        return data

if __name__ == "__main__":
    root = tk.Tk()
    app = GradingApp(root)
    root.mainloop()

