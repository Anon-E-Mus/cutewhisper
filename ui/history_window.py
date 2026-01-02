"""
History Window - View and manage transcription history
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging

logger = logging.getLogger(__name__)


class HistoryWindow:
    """Transcription history viewer"""

    def __init__(self, history_manager, parent=None):
        """
        Initialize history window

        Args:
            history_manager: HistoryManager instance
            parent: Parent tkinter window
        """
        self.history_manager = history_manager
        self.parent = parent
        self.window = None
        self.search_var = None
        self.tree = None

    def show(self):
        """Show history window"""
        if self.window:
            self.window.lift()
            return

        if self.parent:
            self.window = tk.Toplevel(self.parent)
        else:
            self.window = tk.Tk()

        self.window.title("Transcription History")
        self.window.geometry("900x600")
        self.window.resizable(True, True)

        self.create_widgets()
        self.load_history()

        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Create all widgets"""
        # Top frame - search and actions
        top_frame = tk.Frame(self.window)
        top_frame.pack(fill='x', padx=10, pady=10)

        # Search
        search_frame = tk.Frame(top_frame)
        search_frame.pack(side='left', fill='x', expand=True)

        tk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)

        # Clear button
        ttk.Button(top_frame, text="Clear History", command=self.clear_history).pack(side='right', padx=5)

        # Treeview for list
        tree_frame = tk.Frame(self.window)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('timestamp', 'text', 'language')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)

        self.tree.heading('timestamp', text='Date/Time')
        self.tree.heading('text', text='Transcription')
        self.tree.heading('language', text='Lang')

        self.tree.column('timestamp', width=180)
        self.tree.column('text', width=550)
        self.tree.column('language', width=80)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Buttons frame
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Copy Selected", command=self.copy_selected).pack(side='left', padx=5)
        ttk.Button(button_frame, text="View Full Text", command=self.view_full_text).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export All", command=self.export_all).pack(side='right', padx=5)

        # Add close button at bottom
        close_button = ttk.Button(self.window, text="Close", command=lambda: self.on_close())
        close_button.pack(pady=5)

        # Handle window close button (X)
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.on_close())

    def on_close(self):
        """Handle window close"""
        if self.window:
            try:
                self.window.destroy()
            except:
                pass
            self.window = None

    def load_history(self, search=None):
        """Load history into treeview"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load from database
        results = self.history_manager.get_all(limit=200, search=search)

        if not results:
            self.tree.insert('', 'end', values=('', 'No transcriptions found', ''))
            return

        for row in results:
            id, timestamp, text, language, duration, audio_file = row
            # Format timestamp
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_time = timestamp.split('T')[0] if 'T' in timestamp else timestamp

            # Truncate text for display
            display_text = text[:80] + '...' if len(text) > 80 else text

            # Clean up text for display (remove newlines)
            display_text = display_text.replace('\n', ' ').replace('\r', ' ')

            self.tree.insert('', 'end', values=(formatted_time, display_text, language), tags=(str(id),))

    def on_search(self, event):
        """Handle search"""
        search_text = self.search_var.get().strip()
        self.load_history(search=search_text if search_text else None)

    def copy_selected(self):
        """Copy selected text to clipboard"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a transcription to copy.")
            return

        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if not tags:
            return

        id = tags[0]

        # Get full text from database
        result = self.history_manager.get_by_id(int(id))
        if result:
            text = result[2]
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
            messagebox.showinfo("Copied", "Text copied to clipboard!")

    def view_full_text(self):
        """View full text of selected transcription"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a transcription to view.")
            return

        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if not tags:
            return

        id = tags[0]

        # Get full text from database
        result = self.history_manager.get_by_id(int(id))
        if result:
            id, timestamp, text, language, duration, audio_file = result

            # Create view window
            view_window = tk.Toplevel(self.window)
            view_window.title("Full Transcription")
            view_window.geometry("600x400")

            # Add timestamp and language
            info_frame = tk.Frame(view_window)
            info_frame.pack(fill='x', padx=10, pady=10)

            tk.Label(info_frame, text=f"Language: {language.upper()}", font=('Arial', 10, 'bold')).pack(side='left')

            # Scrolled text
            text_widget = tk.Text(view_window, wrap='word', padx=10, pady=10)
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', text)
            text_widget.config(state='disabled')

            # Copy button
            tk.Button(view_window, text="Copy to Clipboard", command=lambda: self._copy_text_to_clipboard(text)).pack(pady=10)

    def _copy_text_to_clipboard(self, text):
        """Helper to copy text to clipboard"""
        self.window.clipboard_clear()
        self.window.clipboard_append(text)
        messagebox.showinfo("Copied", "Text copied to clipboard!")

    def delete_selected(self):
        """Delete selected entry"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a transcription to delete.")
            return

        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if not tags:
            return

        id = tags[0]

        if messagebox.askyesno("Confirm Delete", "Delete this transcription?"):
            self.history_manager.delete(int(id))
            self.load_history(search=self.search_var.get().strip() or None)
            messagebox.showinfo("Deleted", "Transcription deleted.")

    def clear_history(self):
        """Clear all history"""
        count = self.history_manager.get_count()
        if count == 0:
            messagebox.showinfo("History Empty", "No transcriptions to clear.")
            return

        if messagebox.askyesno("Confirm Clear", f"Clear ALL {count} transcriptions from history?\n\nThis cannot be undone!"):
            self.history_manager.clear_all()
            self.load_history()
            messagebox.showinfo("Cleared", "All transcription history has been cleared.")

    def export_all(self):
        """Export all history to file"""
        count = self.history_manager.get_count()
        if count == 0:
            messagebox.showinfo("History Empty", "No transcriptions to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Export Transcription History"
        )

        if file_path:
            try:
                self.history_manager.export_to_file(file_path)
                messagebox.showinfo("Export Complete", f"Successfully exported {count} transcriptions to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export history:\n{e}")
