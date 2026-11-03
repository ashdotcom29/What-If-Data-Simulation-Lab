import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


APP_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(APP_DIR, "experiment_history.json")


class WhatIfApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WHAT IF? | Data Simulation & Comparison Lab")
        self.root.geometry("1200x780")
        self.root.minsize(1000, 680)
        self.root.configure(bg="#f3f5fb")

        self.original_df = None
        self.current_df = None
        self.current_file = None
        self.scenarios = {}
        self.external_df = None
        self.external_name = None
        self.history = self.load_history()

        self.setup_style()
        self.build_layout()
        self.show_welcome()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook", background="#f3f5fb", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 10), font=("Segoe UI", 10, "bold"),
                        background="#e5e9f5", foreground="#3d4663")
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")],
                  foreground=[("selected", "#5546c7")])
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 9),
                        background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                        background="#e9eaf5", foreground="#303653")
        style.configure("TCombobox", padding=6)
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=(11, 7))
        style.configure("Accent.TButton", background="#6557d2", foreground="white")
        style.map("Accent.TButton", background=[("active", "#5143bb")])
        style.configure("TLabel", background="#ffffff", foreground="#29314d",
                        font=("Segoe UI", 9))
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"),
                        foreground="#252b48")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#737b96")
        style.configure("Card.TLabelframe", background="white", padding=12)
        style.configure("Card.TLabelframe.Label", background="white",
                        foreground="#5546c7", font=("Segoe UI", 10, "bold"))

    def build_layout(self):
        header = tk.Frame(self.root, bg="#252b48", height=82)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="WHAT IF?", bg="#252b48", fg="white",
                 font=("Segoe UI", 23, "bold")).pack(side="left", padx=(25, 12), pady=15)
        tk.Label(header, text="INTERACTIVE DATA SIMULATION & COMPARISON LAB",
                 bg="#252b48", fg="#c9c6ff", font=("Segoe UI", 9, "bold")).pack(
                     side="left", pady=25)
        self.status_var = tk.StringVar(value="No dataset loaded")
        tk.Label(header, textvariable=self.status_var, bg="#252b48", fg="#d8dcf0",
                 font=("Segoe UI", 9)).pack(side="right", padx=22)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=16)

        self.dashboard_tab = tk.Frame(self.notebook, bg="#f3f5fb")
        self.explorer_tab = tk.Frame(self.notebook, bg="#f3f5fb")
        self.lab_tab = tk.Frame(self.notebook, bg="#f3f5fb")
        self.compare_tab = tk.Frame(self.notebook, bg="#f3f5fb")
        self.insights_tab = tk.Frame(self.notebook, bg="#f3f5fb")

        self.notebook.add(self.dashboard_tab, text="  Dashboard  ")
        self.notebook.add(self.explorer_tab, text="  Dataset Explorer  ")
        self.notebook.add(self.lab_tab, text="  Experiment Lab  ")
        self.notebook.add(self.compare_tab, text="  Comparison Studio  ")
        self.notebook.add(self.insights_tab, text="  Insights & Reports  ")

        self.build_dashboard()
        self.build_explorer()
        self.build_lab()
        self.build_comparison()
        self.build_insights()

    def page_heading(self, parent, title, subtitle):
        tk.Label(parent, text=title, bg="#f3f5fb", fg="#252b48",
                 font=("Segoe UI", 19, "bold")).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(parent, text=subtitle, bg="#f3f5fb", fg="#737b96",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=19, pady=(0, 12))

    def card(self, parent, title, value="—"):
        frame = tk.Frame(parent, bg="white", highlightbackground="#e4e7f1",
                         highlightthickness=1)
        tk.Label(frame, text=title.upper(), bg="white", fg="#858ba2",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=15, pady=(13, 3))
        value_label = tk.Label(frame, text=value, bg="white", fg="#5143bb",
                               font=("Segoe UI", 20, "bold"))
        value_label.pack(anchor="w", padx=15, pady=(0, 13))
        return frame, value_label

    def build_dashboard(self):
        self.page_heading(self.dashboard_tab, "Your experiment workspace",
                          "Upload a dataset, change the variables and explore what happens.")
        intro = tk.Frame(self.dashboard_tab, bg="#e9e7ff", padx=22, pady=18)
        intro.pack(fill="x", padx=18, pady=8)
        tk.Label(intro, text="CHANGE THE VARIABLES. EXPLORE THE POSSIBILITIES.",
                 bg="#e9e7ff", fg="#4538a8", font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(intro, text="Run hypothetical experiments on your own CSV data — without changing the original file.",
                 bg="#e9e7ff", fg="#55517d", font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 12))
        ttk.Button(intro, text="＋  Upload a CSV dataset", style="Accent.TButton",
                   command=self.upload_dataset).pack(anchor="w")

        cards = tk.Frame(self.dashboard_tab, bg="#f3f5fb")
        cards.pack(fill="x", padx=18, pady=13)
        self.card_rows, self.rows_value = self.card(cards, "Rows")
        self.card_cols, self.cols_value = self.card(cards, "Columns")
        self.card_scenarios, self.scenarios_value = self.card(cards, "Experiments")
        self.card_history, self.history_value = self.card(cards, "Saved history")
        for i, frame in enumerate([self.card_rows, self.card_cols, self.card_scenarios, self.card_history]):
            frame.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 10, 0))
            cards.grid_columnconfigure(i, weight=1)

        quick = tk.Frame(self.dashboard_tab, bg="white", highlightbackground="#e4e7f1",
                         highlightthickness=1, padx=18, pady=15)
        quick.pack(fill="both", expand=True, padx=18, pady=8)
        tk.Label(quick, text="HOW IT WORKS", bg="white", fg="#252b48",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        steps = [
            ("01  Upload", "Choose a CSV file or try the included sample dataset."),
            ("02  Experiment", "Select a numerical column and apply a change or condition."),
            ("03  Compare", "Compare the original data with one or more scenarios."),
            ("04  Understand", "Review statistics, visualisations and generated observations."),
        ]
        for title, desc in steps:
            row = tk.Frame(quick, bg="white")
            row.pack(fill="x", pady=7)
            tk.Label(row, text=title, width=16, anchor="w", bg="white",
                     fg="#5546c7", font=("Segoe UI", 10, "bold")).pack(side="left")
            tk.Label(row, text=desc, bg="white", fg="#606983",
                     font=("Segoe UI", 9)).pack(side="left")

    def build_explorer(self):
        self.page_heading(self.explorer_tab, "Dataset Explorer",
                          "Inspect the structure and basic statistics of your active dataset.")
        bar = tk.Frame(self.explorer_tab, bg="#f3f5fb")
        bar.pack(fill="x", padx=18, pady=(0, 10))
        ttk.Button(bar, text="Upload CSV", style="Accent.TButton",
                   command=self.upload_dataset).pack(side="left")
        ttk.Button(bar, text="Load sample dataset",
                   command=self.load_sample).pack(side="left", padx=8)
        self.dataset_info = tk.StringVar(value="No dataset loaded yet.")
        tk.Label(bar, textvariable=self.dataset_info, bg="#f3f5fb",
                 fg="#737b96").pack(side="right")

        self.preview_frame = tk.Frame(self.explorer_tab, bg="white")
        self.preview_frame.pack(fill="both", expand=True, padx=18, pady=5)
        self.preview_tree = self.make_tree(self.preview_frame)

        self.stats_frame = tk.Frame(self.explorer_tab, bg="white")
        self.stats_frame.pack(fill="x", padx=18, pady=(8, 15))
        tk.Label(self.stats_frame, text="NUMERICAL SUMMARY", bg="white",
                 fg="#5546c7", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=8)
        self.stats_text = tk.Text(self.stats_frame, height=7, wrap="none",
                                  font=("Consolas", 9), bg="#fbfbfe", fg="#343b56",
                                  relief="flat")
        self.stats_text.pack(fill="x", padx=12, pady=(0, 10))

    def make_tree(self, parent):
        holder = tk.Frame(parent, bg="white")
        holder.pack(fill="both", expand=True, padx=8, pady=8)
        tree = ttk.Treeview(holder, show="headings")
        yscroll = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(holder, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        holder.rowconfigure(0, weight=1)
        holder.columnconfigure(0, weight=1)
        return tree

    def fill_tree(self, tree, df, max_rows=100):
        tree.delete(*tree.get_children())
        cols = [str(c) for c in df.columns]
        tree["columns"] = cols
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=max(110, min(190, len(col) * 10 + 30)), anchor="center")
        for _, row in df.head(max_rows).iterrows():
            values = []
            for value in row.tolist():
                if pd.isna(value):
                    values.append("")
                else:
                    values.append(str(value)[:80])
            tree.insert("", "end", values=values)

    def build_lab(self):
        self.page_heading(self.lab_tab, "Experiment Lab",
                          "Create a hypothetical scenario. Your original dataset is never overwritten.")
        container = tk.Frame(self.lab_tab, bg="#f3f5fb")
        container.pack(fill="both", expand=True, padx=18, pady=4)

        controls = tk.LabelFrame(container, text="  CREATE AN EXPERIMENT  ",
                                 bg="white", fg="#5546c7", font=("Segoe UI", 10, "bold"),
                                 padx=15, pady=12)
        controls.pack(fill="x")
        self.scenario_name = tk.StringVar(value="My experiment")
        self.target_var = tk.StringVar()
        self.operation_var = tk.StringVar(value="Increase (%)")
        self.amount_var = tk.StringVar(value="10")
        self.condition_col = tk.StringVar(value="None")
        self.condition_op = tk.StringVar(value="equals")
        self.condition_value = tk.StringVar()

        grid = tk.Frame(controls, bg="white")
        grid.pack(fill="x")
        self.add_form_field(grid, "Scenario name", ttk.Entry(grid, textvariable=self.scenario_name, width=24), 0, 0)
        self.target_combo = ttk.Combobox(grid, textvariable=self.target_var, state="readonly", width=22)
        self.add_form_field(grid, "Target numeric column", self.target_combo, 0, 1)
        self.operation_combo = ttk.Combobox(grid, textvariable=self.operation_var, state="readonly",
            values=["Increase (%)", "Decrease (%)", "Add value", "Subtract value",
                    "Multiply by", "Filter rows (keep match)", "Remove matching rows"], width=25)
        self.add_form_field(grid, "Operation", self.operation_combo, 0, 2)
        self.amount_entry = ttk.Entry(grid, textvariable=self.amount_var, width=18)
        self.add_form_field(grid, "Amount", self.amount_entry, 1, 0)

        self.condition_combo = ttk.Combobox(grid, textvariable=self.condition_col, state="readonly", width=22)
        self.add_form_field(grid, "Optional condition column", self.condition_combo, 1, 1)
        self.condition_op_combo = ttk.Combobox(grid, textvariable=self.condition_op, state="readonly",
            values=["equals", "not equals", "greater than", "less than", "contains"], width=18)
        self.add_form_field(grid, "Condition", self.condition_op_combo, 1, 2)
        self.condition_entry = ttk.Entry(grid, textvariable=self.condition_value, width=18)
        self.add_form_field(grid, "Condition value", self.condition_entry, 2, 0)

        ttk.Button(controls, text="Run experiment", style="Accent.TButton",
                   command=self.run_experiment).pack(anchor="w", pady=(12, 3))

        lower = tk.Frame(container, bg="#f3f5fb")
        lower.pack(fill="both", expand=True, pady=12)
        left = tk.LabelFrame(lower, text="  SAVED SCENARIOS  ", bg="white", fg="#5546c7",
                             font=("Segoe UI", 9, "bold"), padx=10, pady=8)
        left.pack(side="left", fill="y", padx=(0, 10))
        self.scenario_list = tk.Listbox(left, width=28, height=15, font=("Segoe UI", 9),
                                        relief="flat", bg="#fbfbfe", selectbackground="#6557d2")
        self.scenario_list.pack(fill="both", expand=True)
        self.scenario_list.bind("<<ListboxSelect>>", self.select_scenario)
        ttk.Button(left, text="Export selected CSV", command=self.export_scenario).pack(fill="x", pady=(8, 0))

        right = tk.LabelFrame(lower, text="  MODIFIED DATA PREVIEW  ", bg="white", fg="#5546c7",
                              font=("Segoe UI", 9, "bold"), padx=8, pady=8)
        right.pack(side="left", fill="both", expand=True)
        self.scenario_tree = self.make_tree(right)

    def add_form_field(self, parent, label, widget, row, col):
        tk.Label(
            parent,
            text=label,
            bg="white",
            fg="#606983",
            font=("Segoe UI", 8, "bold")
        ).grid(row=row * 2, column=col, sticky="w", padx=6, pady=(6, 2))

        widget.grid(
            row=row * 2 + 1,
            column=col,
            sticky="ew",
            padx=6,
            pady=(0, 8)
        )

        parent.grid_columnconfigure(col, weight=1)
    
    def build_comparison(self):
        self.page_heading(self.compare_tab, "Comparison Studio",
                          "Compare the original dataset with a saved scenario or a second CSV file.")
        controls = tk.Frame(self.compare_tab, bg="#f3f5fb")
        controls.pack(fill="x", padx=18, pady=4)
        tk.Label(controls, text="Scenario:", bg="#f3f5fb", fg="#606983").pack(side="left")
        self.compare_scenario_var = tk.StringVar()
        self.compare_scenario_combo = ttk.Combobox(controls, textvariable=self.compare_scenario_var,
                                                   state="readonly", width=28)
        self.compare_scenario_combo.pack(side="left", padx=7)
        ttk.Button(controls, text="Load second CSV", command=self.load_second_csv).pack(side="left", padx=8)
        self.external_label = tk.StringVar(value="No second dataset loaded")
        tk.Label(controls, textvariable=self.external_label, bg="#f3f5fb",
                 fg="#737b96").pack(side="left", padx=8)

        self.compare_summary = tk.Text(self.compare_tab, height=9, wrap="word",
            font=("Segoe UI", 10), bg="white", fg="#343b56", relief="flat",
            padx=14, pady=12)
        self.compare_summary.pack(fill="x", padx=18, pady=10)
        plot_box = tk.Frame(self.compare_tab, bg="white")
        plot_box.pack(fill="both", expand=True, padx=18, pady=(0, 15))
        self.compare_plot_frame = plot_box
        self.compare_canvas = None
        ttk.Button(controls, text="Compare now", style="Accent.TButton",
                   command=self.compare_now).pack(side="left", padx=8)

    def build_insights(self):
        self.page_heading(self.insights_tab, "Insights & Reports",
                          "Review findings from your active comparison and export your work.")
        self.insight_text = tk.Text(self.insights_tab, height=20, wrap="word",
            font=("Segoe UI", 10), bg="white", fg="#343b56", relief="flat",
            padx=18, pady=16)
        self.insight_text.pack(fill="both", expand=True, padx=18, pady=8)
        buttons = tk.Frame(self.insights_tab, bg="#f3f5fb")
        buttons.pack(fill="x", padx=18, pady=(0, 15))
        ttk.Button(buttons, text="Generate insights", style="Accent.TButton",
                   command=self.generate_insights).pack(side="left")
        ttk.Button(buttons, text="Export text report", command=self.export_report).pack(side="left", padx=8)
        ttk.Button(buttons, text="Export active dataset", command=self.export_active).pack(side="left")

    def show_welcome(self):
        self.refresh_dashboard()

    def upload_dataset(self):
        path = filedialog.askopenfilename(title="Choose a CSV dataset",
                                          filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            df = pd.read_csv(path)
            if df.empty or len(df.columns) == 0:
                raise ValueError("The selected CSV file is empty.")
            self.set_dataset(df, path)
        except Exception as exc:
            messagebox.showerror("Could not load dataset", str(exc))

    def load_sample(self):
        path = os.path.join(APP_DIR, "data", "sample_student_data.csv")
        try:
            df = pd.read_csv(path)
            self.set_dataset(df, path)
        except Exception as exc:
            messagebox.showerror("Sample unavailable", str(exc))

    def set_dataset(self, df, path=None):
        self.original_df = df.copy()
        self.current_df = df.copy()
        self.current_file = path or "Uploaded dataset"
        self.scenarios.clear()
        self.scenario_list.delete(0, "end")
        self.external_df = None
        self.external_name = None
        self.external_label.set("No second dataset loaded")
        self.status_var.set(os.path.basename(path) if path else "Dataset loaded")
        self.dataset_info.set(f"{len(df):,} rows  •  {len(df.columns)} columns")
        self.fill_tree(self.preview_tree, df)
        self.update_stats()
        numeric = list(df.select_dtypes(include=np.number).columns)
        self.target_combo["values"] = numeric
        self.target_var.set(str(numeric[0]) if numeric else "")
        self.condition_combo["values"] = ["None"] + [str(c) for c in df.columns]
        self.condition_col.set("None")
        self.refresh_scenario_controls()
        self.refresh_dashboard()
        self.compare_summary.delete("1.0", "end")
        self.compare_summary.insert("end", "Dataset loaded. Select a scenario and click Compare now.")
        self.insight_text.delete("1.0", "end")
        self.insight_text.insert("end", "Your insights will appear here after you run an experiment.")
        self.notebook.select(self.explorer_tab)

    def update_stats(self):
        self.stats_text.delete("1.0", "end")
        if self.original_df is None:
            return
        numeric = self.original_df.select_dtypes(include=np.number)
        if numeric.empty:
            self.stats_text.insert("end", "No numerical columns found in this dataset.")
        else:
            self.stats_text.insert("end", numeric.describe().round(2).to_string())

    def refresh_dashboard(self):
        if self.original_df is not None:
            self.rows_value.config(text=f"{len(self.original_df):,}")
            self.cols_value.config(text=str(len(self.original_df.columns)))
        self.scenarios_value.config(text=str(len(self.scenarios)))
        self.history_value.config(text=str(len(self.history)))

    def refresh_scenario_controls(self):
        names = list(self.scenarios.keys())
        self.scenario_list.delete(0, "end")
        for name in names:
            self.scenario_list.insert("end", name)
        self.compare_scenario_combo["values"] = names
        if names and self.compare_scenario_var.get() not in names:
            self.compare_scenario_var.set(names[-1])
        elif not names:
            self.compare_scenario_var.set("")
        self.refresh_dashboard()

    def condition_mask(self, df):
        col = self.condition_col.get()
        if col == "None" or not col:
            return pd.Series(True, index=df.index)
        if col not in df.columns:
            raise ValueError("Choose a valid condition column.")
        raw = self.condition_value.get().strip()
        if raw == "":
            raise ValueError("Enter a condition value, or set condition column to None.")
        series = df[col]
        op = self.condition_op.get()
        if op in ("greater than", "less than"):
            try:
                val = float(raw)
                values = pd.to_numeric(series, errors="coerce")
            except ValueError:
                raise ValueError("Greater than / less than conditions require a numeric value.")
            return values > val if op == "greater than" else values < val
        if op == "equals":
            numeric_val = pd.to_numeric(pd.Series([raw]), errors="coerce").iloc[0]
            if pd.api.types.is_numeric_dtype(series) and not pd.isna(numeric_val):
                return pd.to_numeric(series, errors="coerce") == numeric_val
            return series.astype(str).str.casefold() == raw.casefold()
        if op == "not equals":
            return ~(series.astype(str).str.casefold() == raw.casefold())
        if op == "contains":
            return series.astype(str).str.contains(raw, case=False, na=False, regex=False)
        return pd.Series(True, index=df.index)

    def run_experiment(self):
        if self.original_df is None:
            messagebox.showwarning("No dataset", "Upload a CSV dataset first.")
            return
        name = self.scenario_name.get().strip() or f"Scenario {len(self.scenarios)+1}"
        if name in self.scenarios:
            if not messagebox.askyesno("Replace scenario?", f"'{name}' already exists. Replace it?"):
                return
        try:
            df = self.original_df.copy()
            operation = self.operation_var.get()
            mask = self.condition_mask(df)
            if operation in ("Filter rows (keep match)", "Remove matching rows"):
                if self.condition_col.get() == "None":
                    raise ValueError("Choose a condition column for filtering or removing rows.")
                if operation == "Filter rows (keep match)":
                    result = df.loc[mask].copy()
                else:
                    result = df.loc[~mask].copy()
                description = f"{operation}; condition: {self.condition_col.get()} {self.condition_op.get()} {self.condition_value.get()}"
            else:
                col = self.target_var.get()
                if not col or col not in df.columns:
                    raise ValueError("Select a numerical target column.")
                amount = float(self.amount_var.get())
                values = pd.to_numeric(df[col], errors="coerce")
                if operation == "Increase (%)":
                    df.loc[mask, col] = values.loc[mask] * (1 + amount / 100)
                elif operation == "Decrease (%)":
                    df.loc[mask, col] = values.loc[mask] * (1 - amount / 100)
                elif operation == "Add value":
                    df.loc[mask, col] = values.loc[mask] + amount
                elif operation == "Subtract value":
                    df.loc[mask, col] = values.loc[mask] - amount
                elif operation == "Multiply by":
                    df.loc[mask, col] = values.loc[mask] * amount
                result = df
                condition_desc = "all rows" if self.condition_col.get() == "None" else f"where {self.condition_col.get()} {self.condition_op.get()} {self.condition_value.get()}"
                description = f"{operation} {amount} on '{col}' ({condition_desc})"

            self.scenarios[name] = {"data": result.copy(), "description": description,
                                    "created": datetime.now().strftime("%Y-%m-%d %H:%M")}
            self.current_df = result.copy()
            self.fill_tree(self.scenario_tree, result)
            self.refresh_scenario_controls()
            self.scenario_list.selection_clear(0, "end")
            index = list(self.scenarios.keys()).index(name)
            self.scenario_list.selection_set(index)
            self.compare_scenario_var.set(name)
            self.history.append({"name": name, "description": description,
                                 "created": datetime.now().strftime("%Y-%m-%d %H:%M")})
            self.save_history()
            self.refresh_dashboard()
            messagebox.showinfo("Experiment complete",
                                f"Scenario '{name}' created successfully.\n"
                                f"Rows: {len(self.original_df)} → {len(result)}")
        except Exception as exc:
            messagebox.showerror("Experiment could not run", str(exc))

    def select_scenario(self, event=None):
        selection = self.scenario_list.curselection()
        if not selection:
            return
        name = self.scenario_list.get(selection[0])
        self.current_df = self.scenarios[name]["data"].copy()
        self.fill_tree(self.scenario_tree, self.current_df)
        self.compare_scenario_var.set(name)

    def export_scenario(self):
        selection = self.scenario_list.curselection()
        if not selection:
            messagebox.showinfo("Select a scenario", "Choose a saved scenario first.")
            return
        name = self.scenario_list.get(selection[0])
        self.save_dataframe(self.scenarios[name]["data"], f"{name}.csv")

    def export_active(self):
        if self.current_df is None:
            messagebox.showwarning("No data", "Load a dataset and run an experiment first.")
            return
        self.save_dataframe(self.current_df, "whatif_modified_dataset.csv")

    def save_dataframe(self, df, default_name):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                    initialfile=default_name, filetypes=[("CSV files", "*.csv")])
        if path:
            try:
                df.to_csv(path, index=False)
                messagebox.showinfo("Export complete", f"Saved to:\n{path}")
            except Exception as exc:
                messagebox.showerror("Export failed", str(exc))

    def load_second_csv(self):
        path = filedialog.askopenfilename(title="Choose another CSV file",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            self.external_df = pd.read_csv(path)
            self.external_name = os.path.basename(path)
            self.external_label.set(f"Loaded: {self.external_name}")
            messagebox.showinfo("Second dataset loaded",
                                "Click 'Compare now' to compare common numerical columns.")
        except Exception as exc:
            messagebox.showerror("Could not load second dataset", str(exc))

    def compare_now(self):
        if self.original_df is None:
            messagebox.showwarning("No dataset", "Upload a primary dataset first.")
            return
        scenario_name = self.compare_scenario_var.get()
        if self.external_df is not None:
            other = self.external_df
            other_label = self.external_name or "Second dataset"
        elif scenario_name and scenario_name in self.scenarios:
            other = self.scenarios[scenario_name]["data"]
            other_label = scenario_name
        else:
            messagebox.showwarning("Nothing to compare",
                                   "Create a scenario or load a second CSV file first.")
            return

        common = [c for c in self.original_df.columns if c in other.columns]
        numeric = [c for c in common
                   if pd.api.types.is_numeric_dtype(self.original_df[c])
                   and pd.api.types.is_numeric_dtype(other[c])]
        lines = [f"COMPARISON: Original dataset vs {other_label}",
                 f"Original: {len(self.original_df)} rows × {len(self.original_df.columns)} columns",
                 f"Other:    {len(other)} rows × {len(other.columns)} columns",
                 f"Common columns: {len(common)}",
                 f"Common numerical columns: {len(numeric)}", ""]
        if not numeric:
            lines.append("No common numerical columns were found.")
        else:
            lines.append("NUMERICAL COMPARISON (mean values)")
            for col in numeric:
                a = pd.to_numeric(self.original_df[col], errors="coerce").mean()
                b = pd.to_numeric(other[col], errors="coerce").mean()
                diff = b - a
                pct = (diff / abs(a) * 100) if a != 0 and not pd.isna(a) else np.nan
                pct_text = f"{pct:+.2f}%" if not pd.isna(pct) else "N/A"
                lines.append(f"• {col}: {a:.2f} → {b:.2f} | change {diff:+.2f} ({pct_text})")
        self.compare_summary.delete("1.0", "end")
        self.compare_summary.insert("end", "\n".join(lines))
        self.draw_comparison_plot(self.original_df, other, numeric, other_label)

    def draw_comparison_plot(self, first, second, numeric, second_label):
        if self.compare_canvas:
            self.compare_canvas.get_tk_widget().destroy()
            self.compare_canvas = None
        for child in self.compare_plot_frame.winfo_children():
            child.destroy()
        if not numeric:
            tk.Label(self.compare_plot_frame, text="No common numerical columns to plot.",
                     bg="white", fg="#737b96").pack(pady=30)
            return
        cols = numeric[:8]
        means_a = [pd.to_numeric(first[c], errors="coerce").mean() for c in cols]
        means_b = [pd.to_numeric(second[c], errors="coerce").mean() for c in cols]
        fig, ax = plt.subplots(figsize=(9, 3.4), dpi=100)
        x = np.arange(len(cols))
        width = 0.36
        ax.bar(x - width/2, means_a, width, label="Original")
        ax.bar(x + width/2, means_b, width, label=second_label[:18])
        ax.set_title("Average values: original vs comparison")
        ax.set_xticks(x)
        ax.set_xticklabels([str(c)[:14] for c in cols], rotation=20, ha="right")
        ax.legend()
        ax.grid(axis="y", alpha=0.2)
        fig.tight_layout()
        self.compare_canvas = FigureCanvasTkAgg(fig, master=self.compare_plot_frame)
        self.compare_canvas.draw()
        self.compare_canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def generate_insights(self):
        if self.original_df is None:
            messagebox.showwarning("No dataset", "Upload a dataset first.")
            return
        name = self.compare_scenario_var.get()
        if name not in self.scenarios:
            messagebox.showwarning("No scenario", "Run an experiment and select it in Comparison Studio.")
            return
        modified = self.scenarios[name]["data"]
        original = self.original_df
        lines = [f"WHAT IF? — INSIGHT REPORT", f"Scenario: {name}",
                 f"Operation: {self.scenarios[name]['description']}", "",
                 f"Original rows: {len(original)}",
                 f"Modified rows: {len(modified)}",
                 f"Rows added/removed: {len(modified) - len(original):+}", ""]
        common_numeric = [c for c in original.select_dtypes(include=np.number).columns
                          if c in modified.columns and pd.api.types.is_numeric_dtype(modified[c])]
        lines.append("KEY FINDINGS")
        if not common_numeric:
            lines.append("No common numerical columns available for statistical comparison.")
        for col in common_numeric:
            before = pd.to_numeric(original[col], errors="coerce").mean()
            after = pd.to_numeric(modified[col], errors="coerce").mean()
            if pd.isna(before) or pd.isna(after):
                continue
            change = after - before
            if before != 0:
                pct = change / abs(before) * 100
                lines.append(f"• Average {col}: {before:.2f} → {after:.2f} ({change:+.2f}, {pct:+.2f}%).")
            else:
                lines.append(f"• Average {col}: {before:.2f} → {after:.2f} ({change:+.2f}).")
        if len(modified) < len(original):
            lines.append(f"• {len(original)-len(modified)} record(s) were removed by this scenario.")
        elif len(modified) == len(original):
            lines.append("• The number of records remained unchanged.")
        lines += ["", "NOTE", "These are descriptive comparisons of the modified data. They do not prove that a real-world outcome would change in the same way."]
        self.insight_text.delete("1.0", "end")
        self.insight_text.insert("end", "\n".join(lines))
        self.notebook.select(self.insights_tab)

    def export_report(self):
        content = self.insight_text.get("1.0", "end").strip()
        if not content or "Your insights will appear" in content:
            messagebox.showinfo("No report", "Generate insights before exporting a report.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                initialfile="whatif_experiment_report.txt",
                filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
            messagebox.showinfo("Report exported", f"Saved to:\n{path}")

    def load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                    return json.load(file)
        except Exception:
            pass
        return []

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                json.dump(self.history[-100:], file, indent=4)
        except Exception as exc:
            messagebox.showwarning("History not saved", str(exc))


def main():
    root = tk.Tk()
    app = WhatIfApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
