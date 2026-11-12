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

    def compile(self, source=None, example=None):
        """Build in isolation while preserving example-relative package paths."""
        with tempfile.TemporaryDirectory(prefix="dsrm-test-") as directory:
            output = Path(directory)
            if example is None:
                document = output / "test.tex"
                document.write_text(
                    "\\documentclass{article}\n"
                    "\\usepackage{dsrm}\n"
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

    def test_standalone_example(self):
        self.compile(example="tests/standalone/test.tex")

    def test_ieee_example(self):
        self.compile(example="tests/IEEEcsmag/test.tex")

    def test_all_optional_inputs(self):
        self.compile(source=r"""
\resizebox{\textwidth}{!}{%
\SDR{
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
                        r"\sbox{\diagram}{\SDR{" + "\n".join(phases) + "}}\n"
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
