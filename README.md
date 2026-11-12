# Design Science Research methodology in Latex

This a package that allows you to create Design Science Research diagrams in Latex.

## Installation

Copy the `dsrm.sty` to your project.

## Usage

Write the text

```latex
\SDR{
    \ProblemIdentification[How to edit the DSRM diagrams in \LaTeX]{Research methodology must be included in papers.\\\vspace{8pt}Creating DSRM diagrams in other tools and importing them is labour intensive.}
    \ObjectivesOfTheSolution{The tool should integrate seamlessly in any \LaTeX\ tool, e.g. Overleaf, TexShop\\\vspace{8pt}The tool should have a usable interface, hiding its implementation.}
    \DesignAndDevelopment{Develop the tool that draws the DSRM diagram using TikZ package.}
    \Demonstration{Can type the text and diagram is rendered automatically}
    \Evaluation{Can render the diagram in multiple classes}
    \Communication{Create a \LaTeX\ package}
}
```

gives this result in IEEE Computer Science magazines projects:

![result](assets/result.png)

## Tests

Run the automated suite from the project root:

```sh
python3 -m unittest discover -s tests -v
```

Requires Python 3 and `pdflatex` on your PATH, with the LaTeX packages used
by the examples installed (including TikZ, standalone, and the dependencies
of the bundled IEEE class). No additional Python packages are needed.

The suite compiles the article, standalone, and IEEE examples, exercises
all four optional phase inputs with wrapped and formatted text, and checks
that input boxes grow with their content while preserving width and bottom
padding. Builds use temporary directories and leave the example files untouched.
These checks verify compilation and geometry; visual styling still needs review
of the rendered PDF.
