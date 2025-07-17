"""
Name: Jasdeep Singh
Date: 2024-07-16
Description: A GUI tool for aligning images from multiple runs using Tkinter and PIL.
"""



import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import glob
import json
import numpy as np

class ImageAlignmentTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Alignment Tool")
        self.root.geometry("1200x800")
        
        # Variables
        self.base_directory = ""
        self.run_folders = []
        self.current_run_index = 0
        self.current_run_folder = ""
        
        # Images
        self.single_image = None
        self.series_image = None
        self.single_photo = None
        self.series_photo = None
        
        # Alignment parameters
        self.transparency = tk.DoubleVar(value=0.5)
        self.single_x_offset = tk.IntVar(value=0)
        self.single_y_offset = tk.IntVar(value=0)
        self.series_x_offset = tk.IntVar(value=0)
        self.series_y_offset = tk.IntVar(value=0)
        
        # Display parameters
        self.zoom_factor = tk.DoubleVar(value=1.0)
        self.view_x_offset = tk.IntVar(value=0)
        self.view_y_offset = tk.IntVar(value=0)
        
        # Canvas size
        self.canvas_width = 600
        self.canvas_height = 400
        
        # Output size (all aligned images will be this size)
        self.output_width = 600
        self.output_height = 900
        
        # Store alignment settings for each run
        self.alignment_settings = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Directory selection
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(dir_frame, text="Select Base Directory", 
                  command=self.select_directory).grid(row=0, column=0, padx=(0, 10))
        
        self.dir_label = ttk.Label(dir_frame, text="No directory selected")
        self.dir_label.grid(row=0, column=1, sticky=tk.W)
        
        # Run selection
        run_frame = ttk.Frame(main_frame)
        run_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(run_frame, text="Current Run:").grid(row=0, column=0, padx=(0, 10))
        self.run_label = ttk.Label(run_frame, text="No run loaded")
        self.run_label.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(run_frame, text="Previous Run", 
                  command=self.previous_run).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(run_frame, text="Next Run", 
                  command=self.next_run).grid(row=0, column=3, padx=(0, 10))
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Transparency control
        ttk.Label(control_frame, text="Transparency").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        transparency_scale = ttk.Scale(control_frame, from_=0.0, to=1.0, 
                                     variable=self.transparency, orient=tk.HORIZONTAL,
                                     command=self.update_display)
        transparency_scale.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Zoom control
        ttk.Label(control_frame, text="Zoom").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        zoom_scale = ttk.Scale(control_frame, from_=0.2, to=3.0, 
                              variable=self.zoom_factor, orient=tk.HORIZONTAL,
                              command=self.update_display)
        zoom_scale.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # View centering controls
        ttk.Label(control_frame, text="View Position").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(control_frame, text="View X").grid(row=5, column=0, sticky=tk.W)
        view_x_scale = ttk.Scale(control_frame, from_=-400, to=400, 
                                variable=self.view_x_offset, orient=tk.HORIZONTAL,
                                command=self.update_display)
        view_x_scale.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(control_frame, text="View Y").grid(row=7, column=0, sticky=tk.W)
        view_y_scale = ttk.Scale(control_frame, from_=-400, to=400, 
                                variable=self.view_y_offset, orient=tk.HORIZONTAL,
                                command=self.update_display)
        view_y_scale.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Single image controls
        ttk.Label(control_frame, text="Single.png Position").grid(row=9, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(control_frame, text="X Offset").grid(row=10, column=0, sticky=tk.W)
        single_x_scale = ttk.Scale(control_frame, from_=-200, to=200, 
                                  variable=self.single_x_offset, orient=tk.HORIZONTAL,
                                  command=self.update_display)
        single_x_scale.grid(row=11, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(control_frame, text="Y Offset").grid(row=12, column=0, sticky=tk.W)
        single_y_scale = ttk.Scale(control_frame, from_=-200, to=200, 
                                  variable=self.single_y_offset, orient=tk.HORIZONTAL,
                                  command=self.update_display)
        single_y_scale.grid(row=13, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Series image controls
        ttk.Label(control_frame, text="Series_0.jpg Position").grid(row=14, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(control_frame, text="X Offset").grid(row=15, column=0, sticky=tk.W)
        series_x_scale = ttk.Scale(control_frame, from_=-200, to=200, 
                                  variable=self.series_x_offset, orient=tk.HORIZONTAL,
                                  command=self.update_display)
        series_x_scale.grid(row=16, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(control_frame, text="Y Offset").grid(row=17, column=0, sticky=tk.W)
        series_y_scale = ttk.Scale(control_frame, from_=-200, to=200, 
                                  variable=self.series_y_offset, orient=tk.HORIZONTAL,
                                  command=self.update_display)
        series_y_scale.grid(row=18, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Reset button
        ttk.Button(control_frame, text="Reset Alignment", 
                  command=self.reset_alignment).grid(row=19, column=0, pady=(0, 10))
        
        # Apply button
        ttk.Button(control_frame, text="Apply to All Images in Run", 
                  command=self.apply_alignment).grid(row=20, column=0, pady=(0, 10))
        
        # Save all button
        ttk.Button(control_frame, text="Save All Processed Images", 
                  command=self.save_all_processed).grid(row=21, column=0, pady=(0, 10))
        
        # Configure control frame column weight
        control_frame.columnconfigure(0, weight=1)
        
        # Canvas for image display
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, 
                               height=self.canvas_height, bg='white')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure canvas frame weights
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.base_directory = directory
            self.dir_label.config(text=f"Directory: {directory}")
            self.find_run_folders()
            
    def find_run_folders(self):
        """Find all run folders in the base directory"""
        if not self.base_directory:
            return
            
        # Look for folders named "run" followed by numbers
        pattern = os.path.join(self.base_directory, "run*")
        all_folders = glob.glob(pattern)
        
        # Filter to only include folders that contain both required images
        self.run_folders = []
        for folder in all_folders:
            if os.path.isdir(folder):
                single_path = os.path.join(folder, "single.png")
                series_path = os.path.join(folder, "series_0.jpg")
                if os.path.exists(single_path) and os.path.exists(series_path):
                    self.run_folders.append(folder)
        
        # Sort numerically
        self.run_folders.sort(key=lambda x: int(os.path.basename(x).replace('run', '')))
        
        if self.run_folders:
            self.current_run_index = 0
            self.load_current_run()
        else:
            messagebox.showwarning("No Runs Found", 
                                 "No run folders with both single.png and series_0.jpg found.")
            
    def load_current_run(self):
        """Load the current run's images"""
        if not self.run_folders:
            return
            
        self.current_run_folder = self.run_folders[self.current_run_index]
        run_name = os.path.basename(self.current_run_folder)
        self.run_label.config(text=f"{run_name} ({self.current_run_index + 1}/{len(self.run_folders)})")
        
        # Load existing alignment settings if available
        if run_name in self.alignment_settings:
            settings = self.alignment_settings[run_name]
            self.transparency.set(settings['transparency'])
            self.single_x_offset.set(settings['single_x'])
            self.single_y_offset.set(settings['single_y'])
            self.series_x_offset.set(settings['series_x'])
            self.series_y_offset.set(settings['series_y'])
            # Load view settings if they exist
            if 'zoom_factor' in settings:
                self.zoom_factor.set(settings['zoom_factor'])
                self.view_x_offset.set(settings['view_x'])
                self.view_y_offset.set(settings['view_y'])
        else:
            self.reset_alignment()
        
        # Load images
        try:
            single_path = os.path.join(self.current_run_folder, "single.png")
            series_path = os.path.join(self.current_run_folder, "series_0.jpg")
            
            self.single_image = Image.open(single_path)
            self.series_image = Image.open(series_path)
            
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load images: {str(e)}")
            
    def previous_run(self):
        if self.run_folders and self.current_run_index > 0:
            self.save_current_alignment()
            self.current_run_index -= 1
            self.load_current_run()
            
    def next_run(self):
        if self.run_folders and self.current_run_index < len(self.run_folders) - 1:
            self.save_current_alignment()
            self.current_run_index += 1
            self.load_current_run()
            
    def save_current_alignment(self):
        """Save current alignment settings"""
        if self.current_run_folder:
            run_name = os.path.basename(self.current_run_folder)
            self.alignment_settings[run_name] = {
                'transparency': self.transparency.get(),
                'single_x': self.single_x_offset.get(),
                'single_y': self.single_y_offset.get(),
                'series_x': self.series_x_offset.get(),
                'series_y': self.series_y_offset.get(),
                'zoom_factor': self.zoom_factor.get(),
                'view_x': self.view_x_offset.get(),
                'view_y': self.view_y_offset.get()
            }
            
    def reset_alignment(self):
        """Reset all alignment parameters to default"""
        self.transparency.set(0.5)
        self.single_x_offset.set(0)
        self.single_y_offset.set(0)
        self.series_x_offset.set(0)
        self.series_y_offset.set(0)
        self.zoom_factor.set(1.0)
        self.view_x_offset.set(0)
        self.view_y_offset.set(0)
        self.update_display()
        
    def update_display(self, *args):
        """Update the canvas display with overlapped images"""
        if not self.single_image or not self.series_image:
            return
            
        # Clear canvas
        self.canvas.delete("all")
        
        # Get zoom factor
        zoom = self.zoom_factor.get()
        
        # Calculate base scaling to fit canvas (before zoom)
        single_ratio = min(self.canvas_width / self.single_image.width,
                          self.canvas_height / self.single_image.height)
        series_ratio = min(self.canvas_width / self.series_image.width,
                          self.canvas_height / self.series_image.height)
        
        # Use the smaller ratio to ensure both images fit, then apply zoom
        base_scale_ratio = min(single_ratio, series_ratio) * 0.6  # Start smaller to leave room for zoom
        scale_ratio = base_scale_ratio * zoom
        
        # Resize images for display
        display_single = self.single_image.resize(
            (int(self.single_image.width * scale_ratio),
             int(self.single_image.height * scale_ratio)),
            Image.Resampling.LANCZOS
        )
        
        display_series = self.series_image.resize(
            (int(self.series_image.width * scale_ratio),
             int(self.series_image.height * scale_ratio)),
            Image.Resampling.LANCZOS
        )
        
        # Create a larger composite image to allow for panning
        composite_width = max(display_single.width, display_series.width) + 800
        composite_height = max(display_single.height, display_series.height) + 800
        
        composite = Image.new('RGBA', (composite_width, composite_height), (255, 255, 255, 0))
        
        # Calculate positions with alignment offsets
        single_x = (composite_width // 2 - display_single.width // 2 + 
                   int(self.single_x_offset.get() * scale_ratio))
        single_y = (composite_height // 2 - display_single.height // 2 + 
                   int(self.single_y_offset.get() * scale_ratio))
        
        series_x = (composite_width // 2 - display_series.width // 2 + 
                   int(self.series_x_offset.get() * scale_ratio))
        series_y = (composite_height // 2 - display_series.height // 2 + 
                   int(self.series_y_offset.get() * scale_ratio))
        
        # Convert to RGBA for transparency
        if display_single.mode != 'RGBA':
            display_single = display_single.convert('RGBA')
        if display_series.mode != 'RGBA':
            display_series = display_series.convert('RGBA')
        
        # Apply transparency to series image
        alpha = int(255 * self.transparency.get())
        display_series_alpha = display_series.copy()
        display_series_alpha.putalpha(alpha)
        
        # Paste images
        composite.paste(display_single, (single_x, single_y), display_single)
        composite.paste(display_series_alpha, (series_x, series_y), display_series_alpha)
        
        # Apply view panning and crop to canvas size
        view_x = (composite_width - self.canvas_width) // 2 + self.view_x_offset.get()
        view_y = (composite_height - self.canvas_height) // 2 + self.view_y_offset.get()
        
        # Ensure view bounds are within composite image
        view_x = max(0, min(view_x, composite_width - self.canvas_width))
        view_y = max(0, min(view_y, composite_height - self.canvas_height))
        
        # Crop to canvas view
        composite = composite.crop((view_x, view_y, 
                                  view_x + self.canvas_width, 
                                  view_y + self.canvas_height))
        
        # Convert to PhotoImage and display
        self.composite_photo = ImageTk.PhotoImage(composite)
        self.canvas.create_image(self.canvas_width // 2, self.canvas_height // 2, 
                                image=self.composite_photo)
        
    def apply_alignment(self):
        """Apply current alignment to all images in the current run"""
        if not self.current_run_folder:
            messagebox.showwarning("No Run Selected", "Please select a run first.")
            return
            
        try:
            # Save current alignment settings
            self.save_current_alignment()
            
            # Calculate the overlap region first
            overlap_bounds = self.calculate_overlap_region()
            if not overlap_bounds:
                messagebox.showwarning("No Overlap", "No overlap region found between the two images.")
                return
            
            # Find all images in the run folder
            image_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg']:
                image_files.extend(glob.glob(os.path.join(self.current_run_folder, ext)))
            
            if not image_files:
                messagebox.showwarning("No Images", "No images found in the current run folder.")
                return
            
            # Create output directory structure
            run_name = os.path.basename(self.current_run_folder)
            output_base = os.path.join(os.path.dirname(self.base_directory), "UNSLICED_NOBLUR_ALIGNED")
            output_dir = os.path.join(output_base, run_name)
            os.makedirs(output_dir, exist_ok=True)
            
            # Process each image
            for image_path in image_files:
                filename = os.path.basename(image_path)
                
                # Load image
                img = Image.open(image_path)
                
                # Determine if this is single.png or series image
                if filename == "single.png":
                    x_offset = self.single_x_offset.get()
                    y_offset = self.single_y_offset.get()
                else:
                    x_offset = self.series_x_offset.get()
                    y_offset = self.series_y_offset.get()
                
                # Apply alignment and crop to overlap region
                aligned_img = self.align_and_crop_to_overlap(img, x_offset, y_offset, overlap_bounds)
                
                # Save aligned image
                output_path = os.path.join(output_dir, filename)
                aligned_img.save(output_path)
            
            messagebox.showinfo("Success", f"Aligned {len(image_files)} images saved to {output_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply alignment: {str(e)}")
    
    def calculate_overlap_region(self):
        """Calculate the overlap region between single.png and series_0.jpg"""
        if not self.single_image or not self.series_image:
            return None
        
        # Get image dimensions
        single_w, single_h = self.single_image.size
        series_w, series_h = self.series_image.size
        
        # Calculate positions with offsets
        single_x = self.single_x_offset.get()
        single_y = self.single_y_offset.get()
        series_x = self.series_x_offset.get()
        series_y = self.series_y_offset.get()
        
        # Calculate bounds for each image
        single_left = single_x
        single_right = single_x + single_w
        single_top = single_y
        single_bottom = single_y + single_h
        
        series_left = series_x
        series_right = series_x + series_w
        series_top = series_y
        series_bottom = series_y + series_h
        
        # Find overlap region
        overlap_left = max(single_left, series_left)
        overlap_right = min(single_right, series_right)
        overlap_top = max(single_top, series_top)
        overlap_bottom = min(single_bottom, series_bottom)
        
        # Check if there's actually an overlap
        if overlap_left >= overlap_right or overlap_top >= overlap_bottom:
            return None
        
        # Calculate overlap center and dimensions
        overlap_width = overlap_right - overlap_left
        overlap_height = overlap_bottom - overlap_top
        overlap_center_x = (overlap_left + overlap_right) // 2
        overlap_center_y = (overlap_top + overlap_bottom) // 2
        
        # Define crop region centered on overlap, with target dimensions
        crop_left = overlap_center_x - self.output_width // 2
        crop_right = overlap_center_x + self.output_width // 2
        crop_top = overlap_center_y - self.output_height // 2
        crop_bottom = overlap_center_y + self.output_height // 2
        
        return {
            'left': crop_left,
            'right': crop_right,
            'top': crop_top,
            'bottom': crop_bottom,
            'width': self.output_width,
            'height': self.output_height
        }
    
    def align_and_crop_to_overlap(self, image, x_offset, y_offset, overlap_bounds):
        """Align image and crop to the overlap region"""
        # Create a larger canvas to accommodate the positioned image
        canvas_width = image.width + abs(x_offset) + self.output_width
        canvas_height = image.height + abs(y_offset) + self.output_height
        canvas = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))
        
        # Calculate position to place the image on the canvas
        paste_x = max(0, -x_offset) + self.output_width // 2
        paste_y = max(0, -y_offset) + self.output_height // 2
        
        # Paste the image onto the canvas
        if image.mode == 'RGBA':
            canvas.paste(image, (paste_x, paste_y), image)
        else:
            canvas.paste(image, (paste_x, paste_y))
        
        # Calculate crop bounds relative to the canvas
        crop_left = paste_x + x_offset + overlap_bounds['left']
        crop_top = paste_y + y_offset + overlap_bounds['top']
        crop_right = crop_left + overlap_bounds['width']
        crop_bottom = crop_top + overlap_bounds['height']
        
        # Ensure crop bounds are within canvas
        crop_left = max(0, min(crop_left, canvas_width - overlap_bounds['width']))
        crop_top = max(0, min(crop_top, canvas_height - overlap_bounds['height']))
        crop_right = crop_left + overlap_bounds['width']
        crop_bottom = crop_top + overlap_bounds['height']
        
        # Crop the image
        cropped = canvas.crop((crop_left, crop_top, crop_right, crop_bottom))
        
        return cropped
        
    def save_all_processed(self):
        """Save all processed images from all runs"""
        if not self.run_folders:
            messagebox.showwarning("No Runs", "No run folders found.")
            return
            
        # Save current alignment first
        self.save_current_alignment()
        
        try:
            total_processed = 0
            output_base = os.path.join(os.path.dirname(self.base_directory), "UNSLICED_NOBLUR_ALIGNED")
            
            for run_folder in self.run_folders:
                run_name = os.path.basename(run_folder)
                
                # Skip if no alignment settings saved
                if run_name not in self.alignment_settings:
                    continue
                
                # Temporarily load this run's settings to calculate overlap
                original_run_folder = self.current_run_folder
                original_single_image = self.single_image
                original_series_image = self.series_image
                
                self.current_run_folder = run_folder
                
                # Load the reference images for this run
                try:
                    single_path = os.path.join(run_folder, "single.png")
                    series_path = os.path.join(run_folder, "series_0.jpg")
                    self.single_image = Image.open(single_path)
                    self.series_image = Image.open(series_path)
                except:
                    continue
                
                settings = self.alignment_settings[run_name]
                
                # Set alignment parameters
                self.single_x_offset.set(settings['single_x'])
                self.single_y_offset.set(settings['single_y'])
                self.series_x_offset.set(settings['series_x'])
                self.series_y_offset.set(settings['series_y'])
                
                # Calculate overlap bounds
                overlap_bounds = self.calculate_overlap_region()
                if not overlap_bounds:
                    continue
                
                # Create run output directory
                run_output_dir = os.path.join(output_base, run_name)
                os.makedirs(run_output_dir, exist_ok=True)
                
                # Find all images in the run
                image_files = []
                for ext in ['*.png', '*.jpg', '*.jpeg']:
                    image_files.extend(glob.glob(os.path.join(run_folder, ext)))
                
                # Process each image
                for image_path in image_files:
                    filename = os.path.basename(image_path)
                    
                    # Load image
                    img = Image.open(image_path)
                    
                    # Determine offset based on filename
                    if filename == "single.png":
                        x_offset = settings['single_x']
                        y_offset = settings['single_y']
                    else:
                        x_offset = settings['series_x']
                        y_offset = settings['series_y']
                    
                    # Apply alignment and crop
                    aligned_img = self.align_and_crop_to_overlap(img, x_offset, y_offset, overlap_bounds)
                    
                    # Save aligned image
                    output_path = os.path.join(run_output_dir, filename)
                    aligned_img.save(output_path)
                    total_processed += 1
                
                # Restore original state
                self.current_run_folder = original_run_folder
                self.single_image = original_single_image
                self.series_image = original_series_image
                    
            messagebox.showinfo("Success", f"Processed {total_processed} images from {len(self.alignment_settings)} runs.\nSaved to: {output_base}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save processed images: {str(e)}")
            # Restore original state in case of error
            self.current_run_folder = original_run_folder
            self.single_image = original_single_image
            self.series_image = original_series_image

def main():
    root = tk.Tk()
    app = ImageAlignmentTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
