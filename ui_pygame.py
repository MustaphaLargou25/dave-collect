"""
Pygame UI Module

Handles the graphical user interface using Pygame for displaying camera feed,
sensor data, and handling user interactions.
"""

import pygame
import numpy as np
from typing import Optional, Dict, Any, Tuple
import cv2


class PygameUI:
    """Manages the Pygame-based user interface."""
    
    def __init__(self, width: int = 800, height: int = 600, title: str = "Data Collection System"):
        """
        Initialize the Pygame UI.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            title: Window title
        """
        self.width = width
        self.height = height
        self.title = title
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.is_initialized = False
        self.font: Optional[pygame.font.Font] = None
        self.font_large: Optional[pygame.font.Font] = None
        
        self.colors = {
            'background': (30, 30, 30),
            'text': (255, 255, 255),
            'text_secondary': (180, 180, 180),
            'success': (0, 255, 0),
            'error': (255, 0, 0),
            'warning': (255, 165, 0),
            'panel': (50, 50, 50)
        }
    
    def initialize(self) -> bool:
        """
        Initialize Pygame and create the window.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(self.title)
            self.clock = pygame.time.Clock()
            
            self.font = pygame.font.Font(None, 24)
            self.font_large = pygame.font.Font(None, 36)
            
            self.is_initialized = True
            print(f"Pygame UI initialized: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            print(f"Error initializing Pygame: {e}")
            return False
    
    def process_events(self) -> Dict[str, Any]:
        """
        Process Pygame events and return user input.
        
        Returns:
            Dict[str, Any]: Dictionary containing event information
        """
        events = {
            'quit': False,
            'key_pressed': None,
            'capture': False,
            'save': False,
            'escape': False,
            'toggle_recording': False,
            'switch_view': None
        }
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events['quit'] = True
            
            elif event.type == pygame.KEYDOWN:
                events['key_pressed'] = event.key
                
                if event.key == pygame.K_ESCAPE:
                    events['escape'] = True
                    events['quit'] = True
                
                elif event.key == pygame.K_SPACE:
                    events['capture'] = True
                
                elif event.key == pygame.K_s:
                    events['save'] = True
                
                elif event.key == pygame.K_r:
                    events['toggle_recording'] = True
                
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    if event.key == pygame.K_1:
                        events['switch_view'] = '1'
                    elif event.key == pygame.K_2:
                        events['switch_view'] = '2'
                    elif event.key == pygame.K_3:
                        events['switch_view'] = '3'
        
        return events
    
    def draw_frame(self, frame: np.ndarray, position: Tuple[int, int] = (10, 10)):
        """
        Draw a camera frame on the screen.
        
        Args:
            frame: OpenCV frame (BGR format)
            position: (x, y) position to draw the frame
        """
        if frame is None or not self.is_initialized:
            return
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.rot90(frame_rgb)
        frame_rgb = np.flipud(frame_rgb)
        
        frame_surface = pygame.surfarray.make_surface(frame_rgb)
        self.screen.blit(frame_surface, position)
    
    def draw_text(self, text: str, position: Tuple[int, int], 
                  color: str = 'text', large: bool = False):
        """
        Draw text on the screen.
        
        Args:
            text: Text to display
            position: (x, y) position
            color: Color key from self.colors
            large: Use large font if True
        """
        if not self.is_initialized:
            return
        
        font = self.font_large if large else self.font
        text_color = self.colors.get(color, self.colors['text'])
        text_surface = font.render(text, True, text_color)
        self.screen.blit(text_surface, position)
    
    def draw_panel(self, rect: Tuple[int, int, int, int], title: Optional[str] = None):
        """
        Draw a panel background.
        
        Args:
            rect: (x, y, width, height) of the panel
            title: Optional title for the panel
        """
        if not self.is_initialized:
            return
        
        pygame.draw.rect(self.screen, self.colors['panel'], rect)
        pygame.draw.rect(self.screen, self.colors['text'], rect, 2)
        
        if title:
            self.draw_text(title, (rect[0] + 10, rect[1] + 5), large=True)
    
    def draw_sensor_data(self, sensor_data: Dict[str, Any], position: Tuple[int, int]):
        """
        Draw sensor data on the screen.
        
        Args:
            sensor_data: Dictionary of sensor readings
            position: (x, y) starting position
        """
        if not self.is_initialized or not sensor_data:
            return
        
        x, y = position
        self.draw_text("Sensor Data:", (x, y), large=True)
        y += 40
        
        for key, value in sensor_data.items():
            text = f"{key}: {value}"
            self.draw_text(text, (x, y), color='text_secondary')
            y += 30
    
    def draw_status(self, status_text: str, position: Tuple[int, int], 
                    status_type: str = 'text'):
        """
        Draw status message.
        
        Args:
            status_text: Status message to display
            position: (x, y) position
            status_type: Type of status ('text', 'success', 'error', 'warning')
        """
        self.draw_text(status_text, position, color=status_type)
    
    def draw_instructions(self, position: Tuple[int, int]):
        """
        Draw control instructions.
        
        Args:
            position: (x, y) starting position
        """
        if not self.is_initialized:
            return
        
        instructions = [
            "Controls:",
            "SPACE - Capture Frame",
            "R - Start/Stop Recording",
            "1/2/3 - Switch View",
            "S - Save Data",
            "ESC - Quit"
        ]
        
        x, y = position
        self.draw_text(instructions[0], (x, y), large=True)
        y += 40
        
        for instruction in instructions[1:]:
            self.draw_text(instruction, (x, y), color='text_secondary')
            y += 30
    
    def clear(self):
        """Clear the screen with background color."""
        if self.is_initialized and self.screen:
            self.screen.fill(self.colors['background'])
    
    def update(self, fps: int = 60):
        """
        Update the display and maintain frame rate.
        
        Args:
            fps: Target frames per second
        """
        if self.is_initialized:
            pygame.display.flip()
            if self.clock:
                self.clock.tick(fps)
    
    def get_fps(self) -> float:
        """
        Get current frame rate.
        
        Returns:
            float: Current FPS
        """
        if self.clock:
            return self.clock.get_fps()
        return 0.0
    
    def quit(self):
        """Quit Pygame and close the window."""
        if self.is_initialized:
            pygame.quit()
            self.is_initialized = False
            print("Pygame UI closed")
    
    def __del__(self):
        """Ensure Pygame is quit when object is destroyed."""
        self.quit()
