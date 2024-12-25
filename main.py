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
        """
        Initialize the GradingApp class with the root window.
        Sets up the initial variables and GUI components.
        """
        self.root = root
        self.root.title("Grading System Application")
        self.root.geometry("500x700")
        self.root.configure(bg="#f5f5f5")
        
        # Variables
        self.grading_type = tk.StringVar(value="absolute")  # Default grading type is 'absolute'
        self.file_path = None  # File path for the uploaded CSV file
        self.data = None  # Placeholder for the data from the CSV

        # GUI Components
        self.create_widgets()

    def create_widgets(self):
        """
        Create and display all the necessary widgets for the user interface.
        """
        # Title label at the top of the window
        title_label = tk.Label(self.root, text="Grading System", font=("Arial", 20, "bold"), bg="#f5f5f5", fg="#333")
        title_label.pack(pady=20)

        # Frame for File Upload Section
        file_frame = tk.Frame(self.root, bg="#e0e0e0", bd=2, relief="groove")
        file_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(file_frame, text="Upload Grades CSV:", font=("Arial", 12), bg="#e0e0e0").pack(pady=10)
        tk.Button(file_frame, text="Upload File", command=self.upload_file, bg="#4caf50", fg="white", font=("Arial", 12), relief="raised").pack(pady=5)

        # Frame for Grading Options Section
        grading_frame = tk.Frame(self.root, bg="#e0e0e0", bd=2, relief="groove")
        grading_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(grading_frame, text="Select Grading Type:", font=("Arial", 12), bg="#e0e0e0").pack(pady=10)
        tk.Radiobutton(grading_frame, text="Absolute Grading", variable=self.grading_type, value="absolute", bg="#e0e0e0", font=("Arial", 11)).pack(anchor="w")
        tk.Radiobutton(grading_frame, text="Relative Grading", variable=self.grading_type, value="relative", bg="#e0e0e0", font=("Arial", 11)).pack(anchor="w")

        # Absolute Grading Thresholds Entry Field
        tk.Label(grading_frame, text="Grade Thresholds (Absolute Grading):", font=("Arial", 12), bg="#e0e0e0").pack(pady=10)
        self.thresholds_entry = tk.Entry(grading_frame, font=("Arial", 11))
        self.thresholds_entry.insert(0, "A:90,B:80,C:70,D:60,F:50")  # Default thresholds
        self.thresholds_entry.pack(fill="x", padx=10, pady=5)

        # Frame for Action Buttons Section
        action_frame = tk.Frame(self.root, bg="#e0e0e0", bd=2, relief="groove")
        action_frame.pack(pady=10, padx=20, fill="x")
        tk.Button(action_frame, text="Process Grades", command=self.process_grades, bg="#2196f3", fg="white", font=("Arial", 12), relief="raised").pack(pady=10)
        tk.Button(action_frame, text="Show Statistics", command=self.show_statistics, bg="#ff9800", fg="white", font=("Arial", 12), relief="raised").pack(pady=10)
        tk.Button(action_frame, text="Visualize Data", command=self.visualize_data, bg="#9c27b0", fg="white", font=("Arial", 12), relief="raised").pack(pady=10)
        tk.Button(action_frame, text="Save Report", command=self.save_report, bg="#f44336", fg="white", font=("Arial", 12), relief="raised").pack(pady=10)

    def upload_file(self):
        """
        Opens a file dialog for the user to upload a CSV file.
        Reads the file into a pandas DataFrame and shows a success message.
        """
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.file_path:
            try:
                self.data = pd.read_csv(self.file_path)  # Load the CSV data into a DataFrame
                messagebox.showinfo("Success", "File uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")

    def process_grades(self):
        """
        Processes the grades based on the selected grading type (absolute or relative).
        """
        if self.data is None:
            messagebox.showerror("Error", "Please upload a valid grades file.")
            return

        grading_type = self.grading_type.get()
        if grading_type == "absolute":
            self.apply_absolute_grading()
        elif grading_type == "relative":
            self.apply_relative_grading()

    def apply_absolute_grading(self):
        """
        Applies absolute grading based on user-defined thresholds.
        """
        try:
            thresholds = self.parse_thresholds(self.thresholds_entry.get())
            self.data["Grade"] = self.data["exam1"].apply(lambda x: self.get_absolute_grade(x, thresholds))
            messagebox.showinfo("Success", "Absolute grading applied successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error in absolute grading: {e}")

    def apply_relative_grading(self):
        """
        Applies relative grading based on the distribution of grades.
        """
        try:
            self.data = self.calculate_relative_grades(self.data)
            messagebox.showinfo("Success", "Relative grading applied successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error in relative grading: {e}")

    def show_statistics(self):
        """
        Displays basic statistical summary and grade distribution for the uploaded data.
        """
        if self.data is None:
            messagebox.showerror("Error", "No data to show statistics for.")
            return

        stats = self.data["exam1"].describe()  # Basic statistics for exam1 scores
        grade_counts = self.data["Grade"].value_counts()  # Count of each grade
        stats_message = stats.to_string() + "\n\nGrade Counts:\n" + grade_counts.to_string()
        messagebox.showinfo("Statistics", stats_message)

    def visualize_data(self):
        """
        Visualizes the grade data using multiple plots (histogram, scatter plot, and pie chart).
        """
        if self.data is None:
            messagebox.showerror("Error", "No data to visualize.")
            return

        # Create a figure with multiple subplots
        fig, axs = plt.subplots(3, 1, figsize=(10, 15))
        
        # Plot the original scores histogram
        axs[0].hist(self.data["exam1"], bins=10, alpha=0.7, color="skyblue", label="Original")
        mean = self.data["exam1"].mean()
        std = self.data["exam1"].std()
        x = np.linspace(self.data["exam1"].min(), self.data["exam1"].max(), 100)
        y = norm.pdf(x, mean, std) * len(self.data["exam1"]) * (self.data["exam1"].max() - self.data["exam1"].min()) / 10
        axs[0].plot(x, y, color="red", label="Normal Distribution")
        axs[0].legend()
        axs[0].set_title("Grade Distribution with Normal Curve")
        axs[0].set_xlabel("Scores")
        axs[0].set_ylabel("Frequency")

        # Scatter plot of scores
        axs[1].scatter(range(len(self.data["exam1"])), self.data["exam1"], alpha=0.7, color="purple")
        axs[1].set_title("Scatter Plot of Scores")
        axs[1].set_xlabel("Student Index")
        axs[1].set_ylabel("Scores")

        # Pie chart for grade distribution
        grade_counts = self.data["Grade"].value_counts()
        axs[2].pie(grade_counts, labels=grade_counts.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.tab10.colors)
        axs[2].set_title("Grade Distribution Pie Chart")

        # Adjust layout and add space between plots
        plt.tight_layout(pad=5.0)  # Increase pad to add space between subplots
        plt.show()

    def save_report(self):
        """
        Opens a save file dialog to save the processed data to a CSV file.
        """
        if self.data is None:
            messagebox.showerror("Error", "No data to save.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if save_path:
            self.data.to_csv(save_path, index=False)  # Save the DataFrame to CSV
            messagebox.showinfo("Success", "Report saved successfully!")

    def parse_thresholds(self, thresholds_str):
        """
        Parses a string of thresholds (e.g., 'A:90,B:80,C:70,D:60,F:50') into a dictionary.
        """
        thresholds = {}
        for pair in thresholds_str.split(","):
            grade, value = pair.split(":")
            thresholds[grade] = float(value)
        return thresholds

    def get_absolute_grade(self, score, thresholds):
        """
        Returns the grade based on the absolute score thresholds.
        """
        for grade, threshold in thresholds.items():
            if score >= threshold:
                return grade
        return "F"  # Return "F" if score is below all thresholds

    def calculate_relative_grades(self, data):
        """
        Calculates grades based on the relative position of the score within the distribution.
        """
        mean = data["exam1"].mean()
        std = data["exam1"].std()

        # Define conditions for relative grading
        conditions = [
            data["exam1"] > mean + 2 * std,  # A*
            (mean + 1.5 * std < data["exam1"]) & (data["exam1"] <= mean + 2 * std),  # A
            (mean + std < data["exam1"]) & (data["exam1"] <= mean + 1.5 * std),  # A-
            (mean + 0.5 * std < data["exam1"]) & (data["exam1"] <= mean + std),  # B+
            (mean - 0.5 * std <= data["exam1"]) & (data["exam1"] <= mean + 0.5 * std),  # B
            (mean - std <= data["exam1"]) & (data["exam1"] < mean - 0.5 * std),  # B-
            (mean - 4 / 3 * std <= data["exam1"]) & (data["exam1"] < mean - std),  # C+
            (mean - 5 / 3 * std <= data["exam1"]) & (data["exam1"] < mean - 4 / 3 * std),  # C
            (mean - 2 * std <= data["exam1"]) & (data["exam1"] < mean - 5 / 3 * std),  # C-
            data["exam1"] < mean - 2 * std  # D
        ]

        grades = ["A*", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D"]
        data["Grade"] = np.select(conditions, grades, default="F")  # Assign grades based on conditions

        return data

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = GradingApp(root)
    root.mainloop()
