from src.equipment.meta_controller import MetaController

USER_INPUT = 'topology' # file name without extension input of the user            

### Network topology parsing and creation
meta_controller = MetaController(USER_INPUT)
meta_controller.Import()
meta_controller.list_controllers()