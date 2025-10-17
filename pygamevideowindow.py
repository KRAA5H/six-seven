import pygame
import cv2
import numpy as np

def play_video_window(video_path="sixsevenvideo.mp4"):
    """
    Opens a new pygame window and plays the specified video file.
    
    Args:
        video_path (str): Path to the video file to play
    """
    # Initialize pygame
    pygame.init()
    
    # Open video with OpenCV
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file '{video_path}'")
        return False
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Create pygame window
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("sixseven vid")
    
    # Clock for controlling frame rate
    clock = pygame.time.Clock()
    
    running = True
    
    while running:
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
        
        # Read frame from video
        ret, frame = cap.read()
        
        if not ret:
            # Video ended, loop back to beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        # Convert frame from BGR (OpenCV) to RGB (pygame)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Rotate frame 90 degrees and flip for pygame surface
        frame_rgb = np.rot90(frame_rgb)
        frame_rgb = np.flipud(frame_rgb)
        
        # Convert to pygame surface
        frame_surface = pygame.surfarray.make_surface(frame_rgb)
        
        # Display the frame
        screen.blit(frame_surface, (0, 0))
        pygame.display.flip()
        
        # Control playback speed
        clock.tick(fps)
    
    # Cleanup
    cap.release()
    pygame.quit()
    
    return True

# Function to call the video player
def open_video():
    """Simple function to open the video in a new window"""
    play_video_window()

# Example usage
if __name__ == "__main__":
    # Call this function to open video in new window
    open_video()