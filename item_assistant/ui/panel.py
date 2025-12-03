"""
Slide-Up Panel UI for Item AI Assistant
Windows desktop UI that slides up from bottom of screen.
"""

import tkinter as tk
from tkinter import font as tkfont
import threading
import time
from typing import Optional, Callable
from item_assistant.ui.state import AssistantState, get_ui_state_manager
from item_assistant.logging import get_logger

logger = get_logger()


class SlideUpPanel:
    """Bottom slide-up panel for assistant status and interaction"""
    
    # Color scheme
    COLORS = {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "idle": "#666666",
        "listening": "#00ff00",
        "thinking": "#ffaa00",
        "speaking": "#0099ff",
        "button_bg": "#333333",
        "button_hover": "#444444",
    }
    
    # Dimensions
    PANEL_WIDTH = 1200
    PANEL_HEIGHT = 140
    HIDDEN_Y_OFFSET = 150  # How far below screen to hide
    ANIMATION_SPEED = 20  # ms per frame
    ANIMATION_STEP = 15  # pixels per frame
    
    def __init__(self, on_mic_click: Optional[Callable] = None):
        """
        Initialize slide-up panel
        
        Args:
            on_mic_click: Callback when mic button is clicked
        """
        self.on_mic_click = on_mic_click
        self.state_manager = get_ui_state_manager()
        
        # Window state
        self.root: Optional[tk.Tk] = None
        self.is_visible = False
        self.target_y = 0
        self.current_y = 0
        self.animation_thread: Optional[threading.Thread] = None
        self.running = False
        self.idle_timeout = 5  # seconds
        self.last_activity_time = time.time()
        
        # UI elements
        self.status_label: Optional[tk.Label] = None
        self.user_text_label: Optional[tk.Label] = None
        self.assistant_text_label: Optional[tk.Label] = None
        self.mic_button: Optional[tk.Button] = None
        
        logger.info("SlideUpPanel initialized")
    
    def initialize(self, idle_timeout: int = 5):
        """
        Initialize the panel window
        
        Args:
            idle_timeout: Seconds before auto-hiding when idle
        """
        try:
            self.idle_timeout = idle_timeout
            self._create_window()
            self._create_widgets()
            self.state_manager.register_listener(self._on_state_change)
            logger.info("✅ SlideUpPanel window created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize SlideUpPanel: {e}")
            raise
    
    def _create_window(self):
        """Create the main window"""
        self.root = tk.Tk()
        self.root.title("Item Assistant")
        self.root.geometry(f"{self.PANEL_WIDTH}x{self.PANEL_HEIGHT}")
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Position window at bottom center, initially hidden
        x = (screen_width - self.PANEL_WIDTH) // 2
        self.current_y = screen_height
        self.target_y = screen_height - self.PANEL_HEIGHT
        
        self.root.geometry(f"+{x}+{int(self.current_y)}")
        
        # Window properties
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-alpha", 0.95)  # Slightly transparent
        self.root.configure(bg=self.COLORS["bg"])
        
        # Remove window decorations on Windows
        try:
            self.root.attributes("-toolwindow", True)
        except:
            pass
    
    def _create_widgets(self):
        """Create UI widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left section: Status indicator
        left_frame = tk.Frame(main_frame, bg=self.COLORS["bg"])
        left_frame.pack(side=tk.LEFT, padx=5)
        
        self.status_dot = tk.Canvas(
            left_frame, width=20, height=20, 
            bg=self.COLORS["bg"], highlightthickness=0
        )
        self.status_dot.pack()
        self._update_status_dot(AssistantState.IDLE)
        
        status_font = tkfont.Font(family="Arial", size=10, weight="bold")
        self.status_label = tk.Label(
            left_frame, text="Idle", font=status_font,
            fg=self.COLORS["idle"], bg=self.COLORS["bg"]
        )
        self.status_label.pack()
        
        # Center section: Messages
        center_frame = tk.Frame(main_frame, bg=self.COLORS["bg"])
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        message_font = tkfont.Font(family="Arial", size=9)
        
        user_label_text = tk.Label(
            center_frame, text="You:", font=message_font,
            fg="#aaaaaa", bg=self.COLORS["bg"]
        )
        user_label_text.pack(anchor=tk.W)
        
        self.user_text_label = tk.Label(
            center_frame, text="(waiting for input)", font=message_font,
            fg=self.COLORS["fg"], bg=self.COLORS["bg"], wraplength=400, justify=tk.LEFT
        )
        self.user_text_label.pack(anchor=tk.W, fill=tk.X)
        
        assistant_label_text = tk.Label(
            center_frame, text="Assistant:", font=message_font,
            fg="#aaaaaa", bg=self.COLORS["bg"]
        )
        assistant_label_text.pack(anchor=tk.W, pady=(5, 0))
        
        self.assistant_text_label = tk.Label(
            center_frame, text="(ready)", font=message_font,
            fg=self.COLORS["fg"], bg=self.COLORS["bg"], wraplength=400, justify=tk.LEFT
        )
        self.assistant_text_label.pack(anchor=tk.W, fill=tk.X)
        
        # Right section: Mic button
        right_frame = tk.Frame(main_frame, bg=self.COLORS["bg"])
        right_frame.pack(side=tk.RIGHT, padx=5)
        
        self.mic_button = tk.Button(
            right_frame, text="🎤\nListen", font=tkfont.Font(family="Arial", size=11),
            bg=self.COLORS["button_bg"], fg=self.COLORS["fg"],
            width=8, height=4, command=self._on_mic_click,
            activebackground=self.COLORS["button_hover"]
        )
        self.mic_button.pack()
    
    def _update_status_dot(self, state: AssistantState):
        """Update status indicator dot color"""
        color_map = {
            AssistantState.IDLE: self.COLORS["idle"],
            AssistantState.LISTENING: self.COLORS["listening"],
            AssistantState.THINKING: self.COLORS["thinking"],
            AssistantState.SPEAKING: self.COLORS["speaking"],
        }
        color = color_map.get(state, self.COLORS["idle"])
        
        self.status_dot.delete("all")
        self.status_dot.create_oval(2, 2, 18, 18, fill=color, outline=color)
    
    def _on_state_change(self, state: AssistantState, 
                        user_text: Optional[str], 
                        assistant_text: Optional[str]):
        """
        Called when assistant state changes
        
        Args:
            state: New assistant state
            user_text: Last user message
            assistant_text: Last assistant response
        """
        if not self.root:
            return
        
        try:
            # Update status
            self.status_label.config(text=state.value)
            self._update_status_dot(state)
            
            # Update messages
            if user_text:
                display_text = user_text[:80] + "..." if len(user_text) > 80 else user_text
                self.user_text_label.config(text=display_text)
            
            if assistant_text:
                display_text = assistant_text[:80] + "..." if len(assistant_text) > 80 else assistant_text
                self.assistant_text_label.config(text=display_text)
            
            # Show/hide panel based on state
            if state == AssistantState.IDLE:
                self.last_activity_time = time.time()
                # Start timer to hide after timeout
                self.root.after(self.idle_timeout * 1000, self._check_hide_on_idle)
            else:
                self.last_activity_time = time.time()
                self.show()
        
        except Exception as e:
            logger.error(f"Error updating panel state: {e}")
    
    def _check_hide_on_idle(self):
        """Check if should hide panel when idle"""
        if self.state_manager.current_state == AssistantState.IDLE:
            elapsed = time.time() - self.last_activity_time
            if elapsed >= self.idle_timeout:
                self.hide()
    
    def _on_mic_click(self):
        """Handle mic button click"""
        logger.info("🎤 Mic button clicked")
        if self.on_mic_click:
            try:
                self.on_mic_click()
            except Exception as e:
                logger.error(f"Error in mic click handler: {e}")
    
    def show(self):
        """Show the panel by sliding up"""
        if self.is_visible:
            return
        
        self.is_visible = True
        self.target_y = self.root.winfo_screenheight() - self.PANEL_HEIGHT
        
        # Start animation thread
        if self.animation_thread is None or not self.animation_thread.is_alive():
            self.animation_thread = threading.Thread(target=self._animate_show, daemon=True)
            self.animation_thread.start()
    
    def hide(self):
        """Hide the panel by sliding down"""
        if not self.is_visible:
            return
        
        self.is_visible = False
        self.target_y = self.root.winfo_screenheight()
        
        # Start animation thread
        if self.animation_thread is None or not self.animation_thread.is_alive():
            self.animation_thread = threading.Thread(target=self._animate_hide, daemon=True)
            self.animation_thread.start()
    
    def _animate_show(self):
        """Animate panel sliding up"""
        while self.current_y > self.target_y and self.is_visible:
            self.current_y = max(self.current_y - self.ANIMATION_STEP, self.target_y)
            self.root.geometry(f"+{self.root.winfo_x()}+{int(self.current_y)}")
            time.sleep(self.ANIMATION_SPEED / 1000.0)
    
    def _animate_hide(self):
        """Animate panel sliding down"""
        screen_height = self.root.winfo_screenheight()
        while self.current_y < screen_height and not self.is_visible:
            self.current_y = min(self.current_y + self.ANIMATION_STEP, screen_height)
            self.root.geometry(f"+{self.root.winfo_x()}+{int(self.current_y)}")
            time.sleep(self.ANIMATION_SPEED / 1000.0)
    
    def start(self):
        """Start the panel event loop"""
        if not self.root:
            self.initialize()
        
        self.running = True
        logger.info("🎨 SlideUpPanel started")
        
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error in panel main loop: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the panel"""
        self.running = False
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            self.root = None
        logger.info("🎨 SlideUpPanel stopped")


# Global panel instance
_panel_instance: Optional[SlideUpPanel] = None


def get_slide_up_panel(on_mic_click: Optional[Callable] = None) -> SlideUpPanel:
    """Get or create the global slide-up panel instance"""
    global _panel_instance
    if _panel_instance is None:
        _panel_instance = SlideUpPanel(on_mic_click=on_mic_click)
    return _panel_instance
