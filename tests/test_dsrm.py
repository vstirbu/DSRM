"""Compilation and layout regression tests; run with unittest discovery."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DsrmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("pdflatex") is None:
            raise RuntimeError("pdflatex is required; install a TeX distribution first")

    def compile(self, source=None, example=None, package_options=""):
        """Build in isolation while preserving example-relative package paths."""
        with tempfile.TemporaryDirectory(prefix="dsrm-test-") as directory:
            output = Path(directory)
            if example is None:
                document = output / "test.tex"
                document.write_text(
                    "\\documentclass{article}\n"
                    f"\\usepackage[{package_options}]{{dsrm}}\n"
                    "\\pagestyle{empty}\n"
                    "\\begin{document}\n" + source + "\n\\end{document}\n",
                    encoding="utf-8",
                )
            else:
                document = ROOT / example
            env = os.environ.copy()
            # A trailing empty entry keeps the distribution's default search path.
            env["TEXINPUTS"] = str(ROOT) + os.pathsep + env.get("TEXINPUTS", "")
            result = subprocess.run(
                [
                    "pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                    "-file-line-error", "-no-shell-escape",
                    f"-output-directory={output}", str(document),
                ],
                cwd=document.parent,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            pdf = output / (document.stem + ".pdf")
            self.assertTrue(pdf.is_file(), result.stdout)
            self.assertGreater(pdf.stat().st_size, 0)
            return (output / (document.stem + ".log")).read_text(errors="replace")

    def test_article_example(self):
        self.compile(example="tests/article/main.tex")

    def test_skill_bundled_assets_match_repository(self):
        assets = ROOT / "skills" / "paper-to-dsr" / "assets"
        for original, bundled in (("dsrm.sty", "dsrm.sty"), ("LICENSE", "LICENSE-LPPL")):
            with self.subTest(asset=bundled):
                self.assertEqual(
                    (assets / bundled).read_bytes(), (ROOT / original).read_bytes(),
                    "Run python3 scripts/sync_skill_assets.py to refresh skill assets",
                )

    def test_skill_templates(self):
        for template in ("single-pass.tex", "iterations.tex"):
            with self.subTest(template=template):
                self.compile(example=f"skills/paper-to-dsr/assets/{template}")

    def test_diagram_has_no_extra_horizontal_space(self):
        log = self.compile(source=r"""
\newsavebox{\diagram}
\makeatletter
\tikzset{every picture/.append style={execute at end picture={%
    \typeout{DSRM-expected=\the\dimexpr\pgf@picmaxx-\pgf@picminx\relax}%
}}}
\makeatother
\sbox{\diagram}{\DSR{
    \ProblemIdentification[Input text]{Phase body.}
    \ObjectivesOfTheSolution{Phase body.}
    \DesignAndDevelopment{Phase body.}
    \Demonstration{Phase body.}
    \Evaluation{Phase body.}
    \Communication{Phase body.}
}}
\typeout{DSRM-width=\the\wd\diagram}
\usebox{\diagram}
""")
        values = {
            key: float(value)
            for key, value in re.findall(r"DSRM-([\w-]+)=([\d.]+)pt", log)
        }
        self.assertEqual(len(values), 2, log)
        self.assertAlmostEqual(values["width"], values["expected"], delta=0.01)

    def test_standalone_example(self):
        self.compile(example="tests/standalone/test.tex")

    def test_iterations_example(self):
        self.compile(example="tests/iterations/test.tex")

    def test_iterations_support_empty_input_flag_and_multiple_diagrams(self):
        self.compile(source=r"""
\dsrmshowemptyinputstrue
\resizebox{\textwidth}{!}{\DSRIterations{
    \Iteration{\DesignAndDevelopment{Develop.}\Evaluation{Evaluate.}}
    \Iteration{\DesignAndDevelopment{Improve.}\Communication{Publish.}}
}}
\dsrmshowemptyinputsfalse
\resizebox{\textwidth}{!}{\DSRIterations{
    \Iteration{\ProblemIdentification{Identify.}\Evaluation{Evaluate.}}
    \Iteration{\ObjectivesOfTheSolution{Refine the objectives.}}
}}
\resizebox{\textwidth}{!}{\DSR{
    \ProblemIdentification{A regular diagram still works.}
    \Communication{Publish.}
}}
""")

    def test_iterations_align_columns_and_size_rows_independently(self):
        log = self.compile(source=r"""
\newsavebox{\diagram}
\newdimen\position
\newcommand{\report}[2]{%
    \pgfextracty{\position}{\pgfpointanchor{dsrm-iteration-#1-phase-#2-north}{center}}%
    \typeout{DSRM-#1-#2-top=\the\position}%
    \pgfextracty{\position}{\pgfpointanchor{dsrm-iteration-#1-phase-#2-south}{center}}%
    \typeout{DSRM-#1-#2-bottom=\the\position}%
    \pgfextractx{\position}{\pgfpointanchor{dsrm-iteration-#1-phase-#2-north}{center}}%
    \typeout{DSRM-#1-#2-x=\the\position}%
}
\makeatletter
\tikzset{every picture/.append style={execute at end picture={%
    \typeout{DSRM-expectedwidth=\the\dimexpr\pgf@picmaxx-\pgf@picminx\relax}%
}}}
\makeatother
\sbox{\diagram}{\DSRIterations{
    \Iteration{
        \ObjectivesOfTheSolution[An input in the unused second column.]{Short body.}
        \DesignAndDevelopment{Short body.}
        \Evaluation{Short body.}
    }
    \Iteration{
        \DesignAndDevelopment{First line\\Second line\\Third line\\Fourth line\\
            Fifth line\\Sixth line\\Seventh line\\Eighth line}
        \Evaluation{Short body.}
        \Communication{Publish the results.}
    }
    \Iteration{\DesignAndDevelopment{Final refinements.}}
    \ifdsrmiterationmeasuring\else
        \report{1}{2}\report{1}{3}\report{1}{5}%
        \report{2}{3}\report{2}{5}\report{2}{6}\report{3}{3}%
    \fi
}}
\typeout{DSRM-width=\the\wd\diagram}
\usebox{\diagram}
""")
        values = {
            key: float(value)
            for key, value in re.findall(r"DSRM-([\w-]+)=(-?[\d.]+)pt", log)
        }
        self.assertEqual(len(values), 23, log)
        cm = 72.27 / 2.54
        for row, phases in ((1, (2, 3, 5)), (2, (3, 5, 6))):
            for phase in phases:
                self.assertAlmostEqual(values[f"{row}-{phase}-top"], values[f"{row}-3-top"], delta=0.01)
                self.assertAlmostEqual(values[f"{row}-{phase}-bottom"], values[f"{row}-3-bottom"], delta=0.01)
        for row in (1, 2):
            self.assertAlmostEqual(values[f"{row}-3-bottom"] - values[f"{row + 1}-3-top"], cm, delta=0.01)
            self.assertAlmostEqual(values[f"{row}-3-x"], values[f"{row + 1}-3-x"], delta=0.01)
        self.assertGreater(values["2-3-top"] - values["2-3-bottom"], 4 * cm)
        self.assertAlmostEqual(values["3-3-top"] - values["3-3-bottom"], 3 * cm, delta=0.01)
        self.assertAlmostEqual(values["width"], values["expectedwidth"], delta=0.01)

    def test_iterations_leave_clearance_for_inputs(self):
        # An input can occupy the next row's column or the feedback arrow's route.
        for input_phase in ("DesignAndDevelopment", "Demonstration"):
            with self.subTest(phase=input_phase):
                tall_input = r"\\".join(["Input line."] * 20)
                source = (
                    r"\newdimen\position\DSRIterations{\Iteration{"
                    + "\\" + input_phase + "[" + tall_input + "]{Short body.}"
                    + r"\Evaluation{Evaluate.}}"
                    + r"\Iteration{\DesignAndDevelopment{Improve.}\Communication{Publish.}}"
                    + r"\ifdsrmiterationmeasuring\else"
                    + rf"\pgfextracty{{\position}}{{\pgfpointanchor{{dsrm-iteration-1-phase-{3 if input_phase == 'DesignAndDevelopment' else 4}-occupied}}{{center}}}}"
                    + r"\typeout{DSRM-inputbottom=\the\position}"
                    + r"\pgfextracty{\position}{\pgfpointanchor{dsrm-iteration-2-phase-3-north}{center}}"
                    + r"\typeout{DSRM-nexttop=\the\position}\fi}"
                )
                log = self.compile(source=source)
                values = {
                    key: float(value)
                    for key, value in re.findall(r"DSRM-([\w-]+)=(-?[\d.]+)pt", log)
                }
                self.assertEqual(len(values), 2, log)
                self.assertAlmostEqual(values["inputbottom"] - values["nexttop"], 72.27 / 2.54, delta=0.01)

    def test_ieee_example(self):
        self.compile(example="tests/IEEEcsmag/test.tex")

    def test_all_optional_inputs(self):
        self.compile(source=r"""
\resizebox{\textwidth}{!}{%
\DSR{
    \ProblemIdentification[Short input]{Identify the problem.}
    \ObjectivesOfTheSolution[First line\\Second line]{Define objectives.}
    \DesignAndDevelopment[\textbf{Formatted input}\par Another paragraph.]
        {Develop the solution.}
    \Demonstration[An input with enough words to wrap across several lines
        within the fixed width of the input box.]{Demonstrate it.}
    \Evaluation{Evaluate it.}
    \Communication{Communicate it.}
}}
""")

    def test_input_boxes_require_text(self):
        commands = (
            "ProblemIdentification", "ObjectivesOfTheSolution",
            "DesignAndDevelopment", "Demonstration",
        )
        diagrams = []
        for index, command in enumerate(commands):
            for label, optional in (("omitted", ""), ("empty", "[]"), ("filled", "[Input text]")):
                marker = f"{index}-{label}"
                diagrams.append(
                    r"\sbox{\diagram}{\DSR{"
                    + "\\" + command + optional + "{Phase body.}"
                    # Without an input, the lowest edge is the phase rectangle at y=0.
                    # Its 0.4pt half-stroke and the upper connector's 0.8pt half-stroke
                    # extend the overall height by 1.2pt.
                    + rf"\typeout{{DSRM-{marker}-expected=\the\dimexpr\phaseboxheight+1cm+1.2pt\relax}}"
                    + "}}\n"
                    + rf"\typeout{{DSRM-{marker}-height=\the\dimexpr\ht\diagram+\dp\diagram\relax}}"
                )
        log = self.compile(source=r"\newsavebox{\diagram}" + "\n".join(diagrams)
                           + r"\usebox{\diagram}")
        values = {
            key: float(value)
            for key, value in re.findall(r"DSRM-([\w-]+)=([\d.]+)pt", log)
        }
        self.assertEqual(len(values), 24, log)
        for index, command in enumerate(commands):
            with self.subTest(phase=command):
                for label in ("omitted", "empty"):
                    self.assertAlmostEqual(
                        values[f"{index}-{label}-height"],
                        values[f"{index}-{label}-expected"], delta=0.01,
                    )
                self.assertGreater(
                    values[f"{index}-filled-height"], values[f"{index}-omitted-height"] + 50,
                )

    def test_show_empty_inputs_flag(self):
        commands = (
            "ProblemIdentification", "ObjectivesOfTheSolution",
            "DesignAndDevelopment", "Demonstration",
        )
        diagrams = [r"\newsavebox{\diagram}"]
        for state in ("enabled", "hidden", "restored"):
            if state == "hidden":
                diagrams.append(r"\begingroup\dsrmshowemptyinputsfalse")
            elif state == "restored":
                diagrams.append(r"\endgroup")
            for index, command in enumerate(commands):
                for label, optional in (("omitted", ""), ("empty", "[]"), ("filled", "[Input text]")):
                    marker = f"{state}-{index}-{label}"
                    diagrams.append(
                        r"\sbox{\diagram}{\DSR{"
                        + "\\" + command + optional + "{Phase body.}"
                        + rf"\typeout{{DSRM-{marker}-expected=\the\dimexpr\phaseboxheight+1cm+1.2pt\relax}}"
                        + "}}\n"
                        + rf"\typeout{{DSRM-{marker}-height=\the\dimexpr\ht\diagram+\dp\diagram\relax}}"
                    )
        diagrams.append(r"\usebox{\diagram}")
        log = self.compile(source="\n".join(diagrams), package_options="showemptyinputs")
        values = {
            key: float(value)
            for key, value in re.findall(r"DSRM-([\w-]+)=([\d.]+)pt", log)
        }
        self.assertEqual(len(values), 72, log)
        for index, command in enumerate(commands):
            with self.subTest(phase=command):
                for label in ("omitted", "empty", "filled"):
                    self.assertAlmostEqual(
                        values[f"enabled-{index}-{label}-height"],
                        values[f"restored-{index}-{label}-height"], delta=0.01,
                    )
                    if label == "filled":
                        self.assertAlmostEqual(
                            values[f"enabled-{index}-{label}-height"],
                            values[f"hidden-{index}-{label}-height"], delta=0.01,
                        )
                    else:
                        self.assertAlmostEqual(
                            values[f"hidden-{index}-{label}-height"],
                            values[f"hidden-{index}-{label}-expected"], delta=0.01,
                        )
                        self.assertAlmostEqual(
                            values[f"enabled-{index}-{label}-height"],
                            values[f"enabled-{index}-{label}-expected"] + 3.5 * 72.27 / 2.54,
                            delta=0.01,
                        )

    def test_input_box_grows_with_text(self):
        log = self.compile(source=r"""
\newsavebox{\diagram}
\newdimen\textbottom
\newdimen\boxbottom
\newcommand{\measureinput}[2]{%
    \sbox{\diagram}{%
        \typeout{DSRM-#1-expected=\the\dimexpr.5em\relax}
        \begin{tikzpicture}[font=\large]
            \sdrmphaseinputt[#2]{1}{Phase body}{}
            \pgfextracty{\textbottom}{\pgfpointanchor{inputtext}{south}}
            \pgfextracty{\boxbottom}{\pgfpointanchor{inputbottom}{center}}
            \typeout{DSRM-#1-padding=\the\dimexpr\textbottom-\boxbottom\relax}
            % Both rectangle strokes are thick (0.8pt), adding 0.4pt at each end.
            \typeout{DSRM-#1-extent=\the\dimexpr\phaseboxheight-\boxbottom+.8pt\relax}
        \end{tikzpicture}%
    }%
    \typeout{DSRM-#1-height=\the\dimexpr\ht\diagram+\dp\diagram\relax}
    \typeout{DSRM-#1-width=\the\wd\diagram}
    \usebox{\diagram}\par
}
\measureinput{short}{Short input}
\measureinput{long}{First line\\Second line\\Third line\\Fourth line\\
    Fifth line\\Sixth line\\Seventh line\\Eighth line}
""")
        values = {
            key: float(value)
            for key, value in re.findall(r"DSRM-([\w-]+)=(-?[\d.]+)pt", log)
        }
        self.assertEqual(len(values), 10, log)
        self.assertGreater(values["long-height"], values["short-height"] + 40)
        self.assertAlmostEqual(values["long-width"], values["short-width"], delta=0.1)
        for size in ("short", "long"):
            self.assertAlmostEqual(
                values[f"{size}-height"], values[f"{size}-extent"], delta=0.01
            )
            self.assertAlmostEqual(
                values[f"{size}-padding"], values[f"{size}-expected"], delta=0.01
            )

    def test_phase_height_follows_each_phase_and_resets(self):
        commands = (
            "ProblemIdentification", "ObjectivesOfTheSolution",
            "DesignAndDevelopment", "Demonstration", "Evaluation", "Communication",
        )
        long_text = r"\\".join(["A line of phase content."] * 16)
        for tall_phase in commands:
            with self.subTest(phase=tall_phase):
                diagrams = []
                for label in ("short", "long", "reset"):
                    phases = []
                    for command in commands:
                        body = long_text if label == "long" and command == tall_phase else "Short body."
                        phases.append("\\" + command + "{" + body + "}")
                        phases.append(
                            rf"\typeout{{DSRM-{label}-phase=\the\phaseboxheight}}"
                        )
                    diagrams.append(
                        r"\sbox{\diagram}{\DSR{" + "\n".join(phases) + "}}\n"
                        + rf"\typeout{{DSRM-{label}-height=\the\dimexpr\ht\diagram+\dp\diagram\relax}}"
                    )
                log = self.compile(source=r"\newsavebox{\diagram}" + "\n".join(diagrams)
                                   + r"\usebox{\diagram}")
                values = {
                    key: float(value)
                    for key, value in re.findall(r"DSRM-([\w-]+)=([\d.]+)pt", log)
                }
                self.assertGreater(values["long-phase"], 7 * 72.27 / 2.54)
                self.assertLess(values["short-phase"], 7 * 72.27 / 2.54)
                self.assertAlmostEqual(values["short-height"], values["reset-height"], delta=0.01)
                self.assertAlmostEqual(
                    values["long-height"] - values["short-height"],
                    values["long-phase"] - values["short-phase"], delta=0.01,
                )
                # The final six measurements come from drawing, after the measuring pass.
                heights = re.findall(r"DSRM-long-phase=([\d.]+)pt", log)[-6:]
                self.assertEqual(len(heights), 6)
                self.assertEqual(len(set(heights)), 1)


if __name__ == "__main__":
    unittest.main()
