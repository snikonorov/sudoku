## About

This is an implementation of a command-line Sudoku game.
The program was tested on Windows 10, Python 3.8.10 and Python 3.12.7.

The code is highly modularized, with modules often used as namespaces. The paradigm is mixed, so as to convey ideas in the most convenient way depending on the application – core logic is written in mostly functional style, while input and program state handling logic is mostly procedural. Classes are also used, but mostly as data structures with methods.  
Exception handling is done by 'Exceptions as Values' approach – it separates the main logic from error handling, while also allowing easier (in my view) integration of the latter in the main flow as development progresses.

## Quickstart

#### 0. System setup check
While the program was tested on Windows, it doesn't explicitly rely on any Windows-specific features,
so it should run on any platform. Python 3.8 or higher is required.

#### 1. (Create and) Activate the environment
Assuming you're on Windows, with an environment freshly created by and IDE and at the project root already (see step 2), you can run `call venv/Scripts/activate`

#### 2. Go to the project root
`./sudoku`, the directory of this file  

#### 3. Run the program:

To run with default arguments:
```
python -m src.main
```

To run in plaintext mode (if the terminal doesn't support color):
```
python -m src.main --mode=text-plain
```

To run with case-insensitive position labels enabled (i.e. so that 'e5' is equivalent to 'E5')
```
python -m src.main --ignore-case
```

For a full list of command line arguments and their usage, run:
```
python -m src.main --help
```

## Project structure

<!--
| Tree     |                  | Notes                      |
|:---------|------------------|:---------------------------|
| /sudoku  |                  | Project root               |
|          | /src             | Source code                |
|          | /tests           | Unit tests (pytest)        |
|          | README.md        | (this file)                |
|          | requirements.txt | List of 3rd-party packages |
-->

<table style="width: 100%; border-collapse: collapse; font-family: sans-serif;">
  <thead>
    <tr style="background-color: #f2f2f2;">
      <th colspan="2" style="border: 1px solid #ddd; padding: 8px; text-align: left;">Tree</th>
      <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="2" style="border: 1px solid #ddd; padding: 8px; font-family: monospace;">/sudoku</td>
      <td style="border: 1px solid #ddd; padding: 8px;">Project root</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px; font-family: monospace;"></td>
      <td style="border: 1px solid #ddd; padding: 8px; font-family: monospace;">/src</td>
      <td style="border: 1px solid #ddd; padding: 8px;">Source code</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px; font-family: monospace;"></td>
      <td style="border: 1px solid #ddd; padding: 8px; font-family: monospace;">/tests</td>
      <td style="border: 1px solid #ddd; padding: 8px;">Unit tests (pytest)</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px; font-family: monospace;"></td>
      <td style="border: 1px solid #ddd; padding: 8px; font-family: monospace;">README.md</td>
      <td style="border: 1px solid #ddd; padding: 8px;">(this file)</td>
    </tr>
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px; font-family: monospace;"></td>
      <td style="border: 1px solid #ddd; padding: 8px; font-family: monospace;">requirements.txt</td>
      <td style="border: 1px solid #ddd; padding: 8px;">List of 3rd-party packages</td>
    </tr>
  </tbody>
</table>
