def render_output(field_list, output_data, output_type: str = 'grid', output_options: list = None):

    """
        Renders output into CSV, HTML, 'Grid' or Pandas format.
        :param field_list: List of fields to display
        :param output_data: Output data contains a list of dictionaries
        :param output_type: Output type ('csv', 'html', 'grid' or 'pandas')
        :param output_options: Output options

        :return: Output in specific format. All output is in string format except 'pandas' which returns a
                   Pandas dataframe object.

        Output options:
          'row_id_column': Includes a numbered column to the left incrementing for every row (applies to all but
                             pandas output),
          'seperator' Includes a seperator for each row (applies only to 'grid' output),
          'unicode', Uses unicode characters when displaying output (applies only to 'grid' output),
          'unicode-bld', Uses wider unicode characters when displaying output (applies only to 'grid' output),
          'unicode-dbl', Uses double unicode characters when displaying output (applies only to 'grid' output)
          'ascii', Uses ASCII characters when displaying output (applies only to 'grid' output)

        Note: Rounded unicode is used when no grid format is specified (i.e.: default.

    """

    if len(output_data) == 0:
        return False, "No results were returned."

    if not output_options:
        output_options = []

    content = ''

    if output_type.lower() not in ['csv', 'grid', 'html', 'pandas']:
        return False, f"The output type of '{output_type}' is not supported."

    if 'row_id_column' in output_options:
        field_list.insert(0, 'No')
        counter = 0
        for item in output_data:
            counter += 1
            item['No'] = counter

    if output_type.lower() == 'html':

        content += '<!DOCTYPE html>\n<html>\n  <head>\n    <link rel="stylesheet" href="styles.css">\n  </head>\n'
        content += '  <body>\n'
        content += "    <table>\n      <thead>\n"
        for field in field_list:
            content += f"        <th>{field}</th>\n"
        content += "      <thead>\n      <tbody>\n"
        for item in output_data:
            content += "        <tr>\n"
            for field in field_list:
                if field in item:
                    if item[field] is None:
                        content += "          <td></td>\n"
                    else:
                        if isinstance(item[field], str) or isinstance(item[field], int):
                            content += f"          <td>{str(item[field]).replace('\n', '<br>')}</td>\n"
                        elif isinstance(item[field], list):
                            content += f"          <td>"
                            for index, i in enumerate(item[field]):
                                content += f"{i}"
                                if index != len(item[field]) - 1:
                                    content += "<br>"
                            content += "</td>\n"

                else:
                    content += "          <td></td>\n"
            content += "        </tr>\n"
        content += "      </tbody>\n    </table>\n"
        content += "  </body>\n</html>\n"

    elif output_type.lower() == 'csv':

        for field in field_list:
            content += f"\"{field}\","
        content = f"{content[:-1]}\n"
        for item in output_data:
            for field in field_list:
                if field in item:
                    if item[field] is None:
                        content += ","
                    elif isinstance(item[field], int) or isinstance(item[field], float):
                        content += f"{item[field]},"
                    else:
                        content += f"\"{item[field]}\","
                else:
                    content += ","
            content = content[:-1] + "\n"

    elif output_type.lower() == 'grid':

        if 'unicode' in output_options:        # Unicode
            chars = ['┌', '─', '┬', '┐', '├', '│', '┼', '┤', '└', '┴', '┘']
        elif 'unicode-bld' in output_options:  # Unicode in bold
            chars = ['┏', '━', '┯', '┓', '┣', '┃', '╋', '┫', '┗', '┻', '┛']
        elif 'unicode-dbl' in output_options:  # Unicode in double lines
            chars = ['╔', '═', '╦', '╗', '╠', '║', '╬', '╣', '╚', '╩', '╝']
        elif 'ascii' in output_options:        # ASCII
            chars = ['+', '-', '+', '+', '+', '|', '+', '+', '+', '+', '+']
        elif 'ascii-h' in output_options:
            chars = ['-', '-', '-', '-', '-', ' ', '-', '-', '-', '-', '-']
        elif 'ascii-v' in output_options:
            chars = ['|', ' ', '|', '|', '|', '|', '|', '|', '|', ' ', '|']
        else:                                  # Default rounded unicode
            chars = [u'\u256d', '─', '┬', u'\u256e', '├', '│', '┼', '┤', u'\u2570', '┴', u'\u256f']

        # Work out grid maximums and other info:
        maximums = {}
        grid = {}

        for item_index, item in enumerate(output_data):
            for col_index, field in enumerate(field_list):
                if field not in item:
                    value = ''  # Unpopulated fields default to blank
                else:
                    value = item[field]
                if field not in maximums:
                    maximums[field] = 0
                if maximums[field] < len(field):
                    maximums[field] = len(field)
                if isinstance(value, list):
                    if len(value) == 0:  # Empty list -> []
                        if maximums[field] < len(n):
                            maximums[field] = len(n)
                        if item_index not in grid:
                            grid[item_index] = {}
                        if field not in grid[item_index]:
                            grid[item_index][field] = {}
                        grid[item_index][field][0] = ''
                    else:
                        for row_index, n in enumerate(value):
                            if maximums[field] < len(n):
                                maximums[field] = len(n)
                            if item_index not in grid:
                                grid[item_index] = {}
                            if field not in grid[item_index]:
                                grid[item_index][field] = {}
                            grid[item_index][field][row_index] = n
                elif isinstance(value, str) or isinstance(value, int):
                    for row_index, n in enumerate(str(value).split('\n')):
                        n = n.replace('\r', '')
                        if maximums[field] < len(n):
                            maximums[field] = len(n)
                        if item_index not in grid:
                            grid[item_index] = {}
                        if field not in grid[item_index]:
                            grid[item_index][field] = {}
                        grid[item_index][field][row_index] = n

        # Create seperator line and work our what header looks like:
        header_line_top = chars[0]  # Row on top of table
        header_list = chars[5]      # Header line containing field Names
        header_line = chars[4]      # Line between rows
        footer_line = chars[8]      # Last line of table

        for field_index, field in enumerate(field_list):
            header_line_top += (
                f"{chars[1]}{chars[1] * maximums[field]}{chars[1]}"
                f"{chars[2] if field_index < len(field_list) - 1 else chars[3]}")
            header_list += f" {field}{' ' * (maximums[field] - len(field))} {chars[5]}"
            header_line += (
                f"{chars[1]}{chars[1] * maximums[field]}{chars[1]}"
                f"{chars[6] if field_index < len(field_list) - 1 else chars[7]}")
            footer_line += (
                f"{chars[1]}{chars[1] * maximums[field]}{chars[1]}"
                f"{chars[9] if field_index < len(field_list) - 1 else chars[10]}")
        content += header_line_top + '\n' + header_list + '\n' + header_line + '\n'

        # Create data section of output:
        for item_index, item in enumerate(grid):
            max_rows = 0

            # Work out how many lines this row will use:
            for field in grid[item]:
                if max_rows < len(grid[item][field]):
                    max_rows = len(grid[item][field])
            for r in range(max_rows):
                item_line = chars[5]
                for index, field in enumerate(grid[item]):
                    if r in grid[item_index][field]:
                        value = grid[item_index][field][r]
                        if value == 'None' or value == '':
                            item_line += f" {' ' * maximums[field]} {chars[5]}"
                        else:
                            item_line += f" {value}{' ' * (maximums[field] - len(str(value)))} {chars[5]}"
                    else:
                        item_line += f" {' ' * maximums[field]} {chars[5]}"
                content += item_line + '\n'
            if 'seperator' in output_options:
                if item_index < len(grid) - 1:
                    content += header_line + '\n'
                else:
                    content += footer_line + '\n'

        if 'seperator' not in output_options:
            content += footer_line

        content = content[:-1] if content[-1] == '\n' else content

    elif output_type.lower() == 'pandas':

        content = pandas.DataFrame(data=output_data, columns=field_list)

    return True, content
