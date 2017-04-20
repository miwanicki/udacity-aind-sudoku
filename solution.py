assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    """This is not an efficient solution, as the code will run twice for
    each pair of naked twins. However, second run will not replace any
    value in the squares. To improve, once could eliminate duplicates from the
    all naked list (look at only one twin from the pair + unit to iterate over)
    """
    # Find all potential candidates, squares with only 2 values
    all_candiates = [box for box in values.keys() if len(values[box]) == 2]
    #print(all_candiates)
    # For each candidate in the list above, for each unit that the box is in
    # for each other box in the set (other than the candidate itself), if the
    # values in the box are equal the values for condidate, return the candidate
    # and the whole unit. In the end you get list of boxes to get values from
    # and the unit to iterate over and remove the values.
    all_naked = [[values[twin],unit] for twin in all_candiates \
        for unit in units[twin] \
        for box in set(unit)-set([twin]) \
        if values[twin] == values[box]]

    #for a in all_naked:
        #print(a)
    # Eliminate the naked twins as possibilities for their peers
    # For every unit from all naked list, iterate through the boxes, for every
    # box, where value is not the same as twin (so that we don't remove values
    # from twin boxes), iterate through values in twin and remove from box.
    for twin,unit in all_naked:
        for box in unit:
            if (values[box] != twin) & (len(values[box]) > 1):
                for to_remove in twin:
                    #print(twin, box, values[box], to_remove)
                    values[box] = values[box].replace(to_remove,'')
    # Return updated values in the end
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    # Function provided on the course page
    return [a+b for a in A for b in B]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
            then the value will be '123456789'.
    """
    # Change grid to list, and replace . with 1..9, then zip with boxes and
    # wrap in dict.
    return dict(zip(boxes,['123456789' if val == '.' else val for val in grid]))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    # Function provided on the course page
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    # Solution from pre-project lessons. Identify boxes with single value,
    # then iterate through their peers and remove the values.
    boxes = [box for box in values.keys() if len(values[box]) == 1]
    for box in boxes:
        to_replace = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(to_replace,'')
    return values

def only_choice(values):
    # Solution from pre-project lessons. Iterate through all the units,
    # for every digit in cols, which are also values, 1..9, get list of
    # possible boxes, if there's only a single box for that digit, set value of
    # that box to this digit.
    for unit in unitlist:
        for digit in cols:
            possible_boxes = [box for box in unit if digit in values[box]]
            if len(possible_boxes) == 1:
                values[possible_boxes[0]] = digit
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() \
            if len(values[box]) == 1])

        # Tested calling functions in different order, but there was no
        # difference in runtime, also it depends on the initial setup on the
        # puzzle

        # Call eliminate function and update the values
        values = eliminate(values)
        # Call only choice function and update the values
        values = only_choice(values)
        # Call naked twins function and update the values
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() \
            if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """Using depth-first search and propagation, create a
    search tree and solve the sudoku.
    """
    # Solution from pre-project lessons. First reduce the puzzles, then
    # recursively, find box with least values remaining and iterate through
    # them (depth-first search, guess one and expand the tree)
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[box]) == 1 for box in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[box]), box) for box in boxes if len(values[box]) > 1)
    # Now use recursion to solve each one of the resulting sudokus, and if
    # one returns a value (not False), return that answer!
    for value in values[s]:
        values_copy = values.copy()
        values_copy[s] = value
        recursive = search(values_copy)
        if recursive:
            return recursive

"""Initial setup, with all the variables created in global scope,
so that they can be accessed from every function, without having to pass
the variables to the functions themselves
"""
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') \
    for cs in ('123','456','789')]

"""Diagonal units (part of the project)
Constraint propagation for diagonal units works the same as with other units,
adding boxes on the diagonal to unitlist. Zipping rows and cols (ABC...),
(123...), and reversed(rows) and cols (IHG...), (123...), and wrapping in list.
Everything else stays the same.
"""
diagonal_units = [[r+c for r,c in list(zip(rows,cols))], \
    [r+c for r,c in list(zip(reversed(rows),cols))]]
unitlist = row_units + column_units + square_units + diagonal_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..
            4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid.
        False if no solution exists.
    """
    # Parse the grid to get the grid in dictionary format
    values = grid_values(grid)
    # Call the recursive function search that will handle all the fitting
    values = search(values)
    return values

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..\
    4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. \
        Not a problem! It is not a requirement.')
