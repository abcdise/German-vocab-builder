import jinja2
from Exercise import ExerciseGatherer
from pathlib import Path

# Set up jinja environment

latex_jinja_env = jinja2.Environment(
    block_start_string = r'\BLOCK{',
    block_end_string = '}',
    variable_start_string = r'\VAR{',
    variable_end_string = '}',
    comment_start_string = r'\#{',
    comment_end_string = '}',
    line_statement_prefix = '%%',
    line_comment_prefix = '%#',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader('../src/resources/Templates')
)


class ExerciseWriter():
    def __init__(self, gatherer: ExerciseGatherer, template_path:str, output_folder:str):
        # The exercise gatherer
        self.gatherer = gatherer
        # The path of the template
        self.template_file = Path(template_path)
        # The path of the output folder
        self.output_folder = Path(output_folder)


    def render_template(self, set_index:int):
        output_file_path = self.output_folder / f'output_{set_index}.tex'
        part_name, exercise = self.gatherer.get_exercise_set(set_index)
        output_dict = exercise.exercise_dict
        self.__render_template(output_file_path=output_file_path, 
                               part_name=part_name,
                               **output_dict
                               )


    def __render_template(self, output_file_path:Path, **kwargs):
        '''
        Create the rendered template and export it.
        '''
        template = latex_jinja_env.get_template(str(self.template_file))
        rendered_template = template.render(**kwargs)
        with open(output_file_path, 'w') as f:
            f.write(rendered_template)

