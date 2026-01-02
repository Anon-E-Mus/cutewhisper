"""
Settings Window - Configuration UI
Thread-safe implementation using Toplevel
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sounddevice as sd

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Settings configuration window"""

    def __init__(self, config, parent=None, on_save_callback=None):
        """
        Args:
            config: Config object
            parent: Parent window (optional, if None creates new Tk)
            on_save_callback: Function to call when settings are saved
        """
        self.config = config
        self.on_save_callback = on_save_callback
        self.window = None
        self.variables = {}
        self.parent = parent

    def show(self):
        """Show settings window"""
        if self.window:
            self.window.lift()
            return

        # CRITICAL FIX: Use Toplevel if parent exists
        if self.parent:
            self.window = tk.Toplevel(self.parent)
            # REMOVED: Don't make modal - causes threading issues
            # self.window.transient(self.parent)
            # self.window.grab_set()
        else:
            self.window = tk.Tk()
            self.window.overrideredirect(False)

        self.window.title("CuteWhisper Settings")
        self.window.geometry("500x600")
        self.window.resizable(False, False)

        # Handle window close button (X)
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.close_window())

        self.create_widgets()

        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

        # REMOVED: Don't wait for window - causes blocking issues
        # if self.parent:
        #     self.window.wait_window(self.window)

    def create_widgets(self):
        """Create all widgets"""
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        general_frame = ttk.Frame(notebook)
        audio_frame = ttk.Frame(notebook)
        whisper_frame = ttk.Frame(notebook)

        notebook.add(general_frame, text='General')
        notebook.add(audio_frame, text='Audio')
        notebook.add(whisper_frame, text='Whisper')

        # Populate tabs
        self.create_general_tab(general_frame)
        self.create_audio_tab(audio_frame)
        self.create_whisper_tab(whisper_frame)

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.close_window).pack(side='right')

    def create_general_tab(self, parent):
        """Create general settings tab"""
        # Hotkey section
        hotkey_frame = ttk.LabelFrame(parent, text="Hotkey", padding=10)
        hotkey_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(hotkey_frame, text="Toggle Hotkey:").grid(row=0, column=0, sticky='w', pady=5)
        hotkey_var = tk.StringVar(value=self.config.get('hotkey.toggle', 'ctrl+space'))
        hotkey_entry = ttk.Entry(hotkey_frame, textvariable=hotkey_var, width=20)
        hotkey_entry.grid(row=0, column=1, sticky='w', pady=5)
        self.variables['hotkey.toggle'] = hotkey_var

        ttk.Label(hotkey_frame, text="(e.g., ctrl+space, alt+shift+d)").grid(row=1, column=0, columnspan=2, sticky='w', pady=0)

        # Clipboard section
        clipboard_frame = ttk.LabelFrame(parent, text="Clipboard", padding=10)
        clipboard_frame.pack(fill='x', padx=10, pady=10)

        preserve_var = tk.BooleanVar(value=self.config.get('clipboard.preserve', True))
        preserve_check = ttk.Checkbutton(clipboard_frame, text="Preserve clipboard content", variable=preserve_var)
        preserve_check.grid(row=0, column=0, sticky='w', pady=5)
        self.variables['clipboard.preserve'] = preserve_var

    def create_audio_tab(self, parent):
        """Create audio settings tab"""
        # Device selection
        device_frame = ttk.LabelFrame(parent, text="Input Device", padding=10)
        device_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(device_frame, text="Microphone:").grid(row=0, column=0, sticky='w', pady=5)

        # Get available devices
        try:
            devices = sd.query_devices()
            input_devices = [d['name'] for d in devices if d['max_input_channels'] > 0]
        except Exception as e:
            logger.warning(f"Could not query audio devices: {e}")
            input_devices = ["Default"]

        current_device = self.config.get('audio.device', 'Default')
        if current_device not in input_devices:
            current_device = input_devices[0] if input_devices else "Default"

        device_var = tk.StringVar(value=current_device)
        device_combo = ttk.Combobox(device_frame, textvariable=device_var,
                                   values=input_devices, width=40, state='readonly')
        device_combo.grid(row=0, column=1, sticky='w', pady=5)
        self.variables['audio.device'] = device_var

        # Sample rate
        ttk.Label(device_frame, text="Sample Rate:").grid(row=1, column=0, sticky='w', pady=5)
        rate_var = tk.StringVar(value=str(self.config.get('audio.sample_rate', 16000)))
        rate_combo = ttk.Combobox(device_frame, textvariable=rate_var,
                                 values=['8000', '16000', '44100', '48000'],
                                 width=10, state='readonly')
        rate_combo.grid(row=1, column=1, sticky='w', pady=5)
        self.variables['audio.sample_rate'] = rate_var

    def create_whisper_tab(self, parent):
        """Create Whisper settings tab"""
        # Model selection
        model_frame = ttk.LabelFrame(parent, text="Model", padding=10)
        model_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(model_frame, text="Model Size:").grid(row=0, column=0, sticky='w', pady=5)
        model_var = tk.StringVar(value=self.config.get('whisper.model_size', 'base'))
        model_combo = ttk.Combobox(model_frame, textvariable=model_var,
                                  values=['tiny', 'base', 'small', 'medium', 'large'],
                                  width=15, state='readonly')
        model_combo.grid(row=0, column=1, sticky='w', pady=5)
        self.variables['whisper.model_size'] = model_var

        ttk.Label(model_frame, text="tiny: fastest, large: most accurate").grid(row=1, column=0, columnspan=2, sticky='w', pady=0)

        # Language
        lang_frame = ttk.LabelFrame(parent, text="Language", padding=10)
        lang_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(lang_frame, text="Language:").grid(row=0, column=0, sticky='w', pady=5)
        lang_var = tk.StringVar(value=self.config.get('whisper.language', 'auto'))
        lang_combo = ttk.Combobox(lang_frame, textvariable=lang_var,
                                 values=['auto', 'en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja'],
                                 width=15, state='readonly')
        lang_combo.grid(row=0, column=1, sticky='w', pady=5)
        self.variables['whisper.language'] = lang_var

        ttk.Label(lang_frame, text="auto = auto-detect language").grid(row=1, column=0, columnspan=2, sticky='w', pady=0)

        # GPU Acceleration section
        gpu_frame = ttk.LabelFrame(parent, text="GPU Acceleration", padding=10)
        gpu_frame.pack(fill='x', padx=10, pady=10)

        # Check for CUDA availability
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            gpu_name = torch.cuda.get_device_name(0) if cuda_available else "Not available"
            cuda_available_str = "Yes" if cuda_available else "No"
        except:
            cuda_available = False
            gpu_name = "PyTorch not available"
            cuda_available_str = "No"

        # GPU status display
        ttk.Label(gpu_frame, text=f"CUDA Available: {cuda_available_str}").grid(row=0, column=0, columnspan=2, sticky='w', pady=5)
        if cuda_available:
            ttk.Label(gpu_frame, text=f"GPU: {gpu_name}", font=('Arial', 8)).grid(row=1, column=0, columnspan=2, sticky='w', pady=0)

        # GPU toggle
        gpu_var = tk.StringVar(value=self.config.get('whisper.device', 'cpu'))
        gpu_check = ttk.Checkbutton(
            gpu_frame,
            text="Use GPU acceleration (CUDA)",
            variable=gpu_var,
            onvalue='cuda',
            offvalue='cpu',
            state='normal' if cuda_available else 'disabled'
        )
        gpu_check.grid(row=2, column=0, columnspan=2, sticky='w', pady=5)
        self.variables['whisper.device'] = gpu_var

        # Install CUDA button or info
        if cuda_available:
            ttk.Label(gpu_frame, text="GPU mode uses float16 for faster inference").grid(row=3, column=0, columnspan=2, sticky='w', pady=0)
        else:
            # Install button
            install_btn = ttk.Button(
                gpu_frame,
                text="Install PyTorch with CUDA",
                command=lambda: self._install_cuda()
            )
            install_btn.grid(row=3, column=0, sticky='w', pady=5)

            ttk.Label(gpu_frame, text="(Click to auto-install GPU support)", foreground='gray').grid(row=3, column=1, sticky='w', pady=5)

    def save_settings(self):
        """Save all settings"""
        try:
            # Check if GPU setting changed
            old_device = self.config.get('whisper.device', 'cpu')
            new_device = self.variables.get('whisper.device', tk.StringVar(value='cpu')).get()
            gpu_changed = (old_device != new_device)

            # Save all variables
            for key, variable in self.variables.items():
                if isinstance(variable, tk.BooleanVar):
                    value = variable.get()
                elif isinstance(variable, tk.StringVar):
                    value = variable.get()
                    # Try to convert to int for numeric values
                    if key == 'audio.sample_rate':
                        value = int(value)
                else:
                    value = variable.get()

                self.config.set(key, value)

            logger.info("Settings saved successfully")

            # Build warning message
            warnings = []
            hotkey = self.config.get('hotkey.toggle')
            original_hotkey = 'ctrl+space'  # Default

            if hotkey != original_hotkey:
                warnings.append("• Hotkey changed")

            if gpu_changed:
                warnings.append("• GPU setting changed")

            # Call callback if provided
            if self.on_save_callback:
                self.on_save_callback()

            # Show success message with restart warning if needed
            if warnings:
                msg = "Settings saved successfully!\n\nIMPORTANT: Restart required for:\n" + "\n".join(warnings)
                messagebox.showwarning("Settings Saved - Restart Required", msg)
            else:
                messagebox.showinfo("Settings", "Settings saved successfully!")

            self.close_window()

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")

    def _install_cuda(self):
        """Auto-install PyTorch with CUDA support"""
        import subprocess
        import sys

        # Ask user permission
        response = messagebox.askyesno(
            "Install GPU Support",
            "This will install PyTorch with CUDA support for GPU acceleration.\n\n"
            "• Faster transcription (5-10x speedup)\n"
            "• Requires ~2GB download\n"
            "• You'll need to restart the application\n\n"
            "Do you want to continue?"
        )

        if not response:
            return

        try:
            # Try to detect CUDA version using nvidia-smi
            cuda_version = "11.8"  # Default fallback
            try:
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader,nounits'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    # Parse driver version to estimate CUDA version
                    driver_version = result.stdout.strip()
                    logger.info(f"Detected NVIDIA driver version: {driver_version}")

                    # Map driver versions to CUDA versions
                    # This is approximate - in reality users should check nvidia-smi directly
                    if driver_version:
                        # For simplicity, default to CUDA 11.8 which has good compatibility
                        cuda_version = "11.8"
            except FileNotFoundError:
                logger.warning("nvidia-smi not found - using default CUDA 11.8")
            except subprocess.TimeoutExpired:
                logger.warning("nvidia-smi timeout - using default CUDA 11.8")
            except Exception as e:
                logger.warning(f"Could not detect CUDA version: {e} - using default")

            # Map to PyTorch wheel index
            cuda_version_map = {
                '11.8': 'cu118',
                '12.1': 'cu121',
                '12.4': 'cu124'
            }
            cuda_suffix = cuda_version_map.get(cuda_version, 'cu118')

            # Show installation message
            messagebox.showinfo(
                "Installing",
                f"Installing PyTorch with CUDA {cuda_version}...\n"
                f"This may take a few minutes.\n\n"
                f"Please wait for the completion message."
            )

            # Get pip path
            pip_path = sys.executable

            # Create installation command - only install torch (Whisper doesn't need torchvision/torchaudio)
            install_cmd = [
                pip_path, '-m', 'pip', 'install', 'torch',
                '--index-url', f'https://download.pytorch.org/whl/{cuda_suffix}',
                '--upgrade'
            ]

            logger.info(f"Installing PyTorch with {cuda_suffix}...")
            logger.info(f"Command: {' '.join(install_cmd)}")

            # Run pip install and capture output
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True
            )

            # Log output for debugging
            if result.stdout:
                logger.info(f"pip stdout: {result.stdout[-1000:]}")  # Last 1000 chars
            if result.stderr:
                logger.error(f"pip stderr: {result.stderr[-1000:]}")

            if result.returncode == 0:
                messagebox.showinfo(
                    "Installation Complete",
                    "PyTorch with CUDA has been installed successfully!\n\n"
                    "Please restart CuteWhisper to use GPU acceleration."
                )
                logger.info("PyTorch with CUDA installed successfully")
            else:
                # Show detailed error message
                error_msg = f"Return code: {result.returncode}\n\n"
                if result.stderr:
                    error_msg += f"Error:\n{result.stderr[-500:]}"
                else:
                    error_msg += "Unknown error. Check logs for details."

                messagebox.showerror(
                    "Installation Failed",
                    f"PyTorch installation failed.\n\n{error_msg}\n\n"
                    "Try installing manually:\n"
                    "1. Open Command Prompt\n"
                    f"2. Run: {pip_path} -m pip install torch --index-url https://download.pytorch.org/whl/{cuda_suffix}\n"
                    "3. Restart CuteWhisper"
                )
                logger.error(f"PyTorch installation failed: {error_msg}")

        except Exception as e:
            logger.error(f"Installation error: {e}", exc_info=True)
            messagebox.showerror(
                "Installation Failed",
                f"Failed to install PyTorch:\n{e}\n\n"
                "Please try installing manually:\n"
                "1. Visit https://pytorch.org/\n"
                "2. Select your CUDA version\n"
                "3. Run the provided pip install command"
            )

    def close_window(self):
        """Close the settings window"""
        if self.window:
            self.window.destroy()
            self.window = None
