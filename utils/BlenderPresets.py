from DataTypes import *

def presets(#object/world settings
    camera_name: str = "Camera",
    world_name: str = "World",
    scene_name: str = "Scene",
    world_material_name: str = "Background", 
    #Render settings
    render_engine: str = "CYCLES",
    device: str = "GPU",
    samples: int = 256 >> 1, 
    transparent_glass: bool = True,
    pixel_filter = "BOX", #box means no filter
    #Output settings 
    resolution_x: int = 540 >> 1,
    resolution_y: int = 540 >> 1,
    resolution_percentage: int = 100,
    file_format: str = "PNG",
    color_mode: str = 'RGBA',
    color_depth: str = "8", 
    #Object settings
    world_color: Vector = (0.0, 0.0, 0.0, 0.0), #Transparent and black
    near_clip: float = 0.001, #Smallest possible to avoid intersection with glass
    #Efficiency settings
    max_glossy: int = 5, #Only one reflection is necessary
    max_transparency: int = 5, #Needed for transparent back-light
    max_transmission: int = 10, #If 5, center of the bubble visible
    max_diffuse: int  = 5, #This image has no diffuse elements
    max_volume: int = 5, #This image has not volumetric effects
    max_total: int = 20 #Arbitary 
    ) -> None:
    """ Sets world conditions to render fast and accurately.
        parameters are self explanatory
        """
        
    #Important variables
    scene = bpy.data.scenes[scene_name]
    render = scene.render
    objects = bpy.data.objects
    cameras = bpy.data.cameras
    worlds = bpy.data.worlds
    camera = cameras.get(camera_name)
    camera_obj = objects.get(camera_name)
    world = worlds.get(world_name)
    world_material = world.node_tree.nodes[world_material_name]
    
    #Render settings 
    render.engine = render_engine
    scene.cycles.device = device
    scene.cycles.film_transparent_glass = transparent_glass
    scene.cycles.pixel_filter_type = pixel_filter
    scene.cycles.samples = samples
    
    
    #Output settings 
    render.resolution_x = resolution_x
    render.resolution_y = resolution_y
    render.resolution_percentage = resolution_percentage
    render.image_settings.file_format = file_format
    render.image_settings.color_mode = color_mode
    render.image_settings.color_depth = color_depth
    
    #Object related settings
    world_material.inputs["Color"].default_value = world_color
    camera.clip_start = near_clip
    
    #Efficiency
    scene.cycles.diffuse_bounces = max_diffuse
    scene.cycles.glossy_bounces = max_glossy
    scene.cycles.transparency_max_bounces = max_transparency
    scene.cycles.transmission_bounces = max_transmission
    scene.cycles.volume_bounces = max_volume
