"""
solver/extractor.py - Autonomous Problem Statement and Specification Extractor.

Extracts structured problem specifications from Guvi CodeKata workspace pages
supporting both live Playwright Page instances and offline HTML snapshots.
Implements multi-strategy parsing (DOM class selectors, labeled heading blocks,
and regex pattern matching) to handle varied Qwik SSR and Markdown renderings.
"""

import html
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class SampleCase:
    """Represents a single input/expected-output test case."""
    input_text: str = ""
    expected_output: str = ""
    case_number: int = 1
    explanation: Optional[str] = None

    @property
    def input_data(self) -> str:
        """Alias for compatibility with test runners."""
        return self.input_text

    @input_data.setter
    def input_data(self, val: str) -> None:
        self.input_text = val

    @property
    def input(self) -> str:
        """Alias for compatibility with test runners."""
        return self.input_text

    @property
    def expected(self) -> str:
        """Alias for compatibility with test runners."""
        return self.expected_output

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_number": self.case_number,
            "input_text": self.input_text,
            "expected_output": self.expected_output,
            "explanation": self.explanation,
        }


@dataclass
class ProblemSpecification:
    """
    Standardized problem specification contract.
    Maintains backward compatibility with E2E harness ProblemSpec NamedTuple
    via property aliases (input_desc, output_desc, sample_input, sample_output).
    """
    title: str = "Unknown"
    description: str = ""
    input_spec: str = ""
    output_spec: str = ""
    sample_cases: List[SampleCase] = field(default_factory=list)
    constraints: str = ""
    category: str = "General"
    raw_text: str = ""
    _slug: str = field(default="", repr=False)

    @property
    def slug(self) -> str:
        """Derives or returns normalized slug."""
        if self._slug:
            return self._slug
        if self.title and self.title != "Unknown":
            cleaned = re.sub(r"^\d+\.\s*", "", self.title)
            return re.sub(r"[^a-z0-9]+", "-", cleaned.lower()).strip("-")
        return ""

    @slug.setter
    def slug(self, val: str) -> None:
        self._slug = val

    @property
    def input_desc(self) -> str:
        """Alias for E2E harness compatibility."""
        return self.input_spec

    @input_desc.setter
    def input_desc(self, val: str) -> None:
        self.input_spec = val

    @property
    def output_desc(self) -> str:
        """Alias for E2E harness compatibility."""
        return self.output_spec

    @output_desc.setter
    def output_desc(self, val: str) -> None:
        self.output_spec = val

    @property
    def sample_input(self) -> str:
        """Primary sample input string."""
        return self.sample_cases[0].input_text if self.sample_cases else ""

    @property
    def sample_output(self) -> str:
        """Primary expected sample output string."""
        return self.sample_cases[0].expected_output if self.sample_cases else ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "input_spec": self.input_spec,
            "output_spec": self.output_spec,
            "sample_cases": [sc.to_dict() for sc in self.sample_cases],
            "sample_input": self.sample_input,
            "sample_output": self.sample_output,
            "constraints": self.constraints,
            "category": self.category,
            "slug": self.slug,
            "raw_text": self.raw_text,
        }


# Canonical alias for PROJECT.md interface contract compatibility
ProblemSpec = ProblemSpecification


class ProblemExtractor:
    """
    Multi-stage problem extractor for Guvi CodeKata DOM structures.
    Uses layered extraction:
      1. Structural DOM / CSS Class Selectors
      2. Semantic Heading & Label Parsing
      3. Regular Expression Pattern Matching on Sanitized Text
    """

    @classmethod
    def extract(cls, source: Any) -> ProblemSpecification:
        """
        Extracts ProblemSpecification from either a Playwright Page or an HTML string.
        """
        if source is None:
            return ProblemSpecification(title="Unknown")

        # 1. Resolve source to HTML string and optional live Page handle
        page = None
        html_text = ""

        if isinstance(source, str):
            html_text = source
        elif hasattr(source, "content") and callable(getattr(source, "content")):
            page = source
            try:
                html_text = source.content()
            except Exception as e:
                logger.warning("Failed to obtain HTML via page.content(): %s", e)
                html_text = ""
        else:
            html_text = str(source)

        if not html_text.strip():
            return ProblemSpecification(title="Unknown")

        # 2. Extract Title
        title = cls._extract_title(html_text, page)

        # 3. Extract Category / Tags / Difficulty
        category = cls._extract_category(html_text, page)

        # 4. Extract Description
        description = cls._extract_description(html_text)

        # 5. Extract Input Specification
        input_spec = cls._extract_input_spec(html_text)

        # 6. Extract Output Specification
        output_spec = cls._extract_output_spec(html_text)

        # 7. Extract Constraints
        constraints = cls._extract_constraints(html_text)

        # 8. Extract Sample Cases (supports multiple cases)
        sample_cases = cls._extract_sample_cases(html_text)

        # 9. Extract Raw Clean Text
        raw_text = cls._clean_text(html_text)

        return ProblemSpecification(
            title=title,
            description=description,
            input_spec=input_spec,
            output_spec=output_spec,
            sample_cases=sample_cases,
            constraints=constraints,
            category=category,
            raw_text=raw_text,
        )

    @classmethod
    def _clean_text(cls, raw_html: str, preserve_newlines: bool = False) -> str:
        """Sanitizes HTML content into clean readable text."""
        if not raw_html:
            return ""
        # Strip script, style, noscript, svg blocks and HTML comments completely
        text = re.sub(r"(?is)<(script|style|noscript|svg)\b[^>]*>.*?</\1>", " ", raw_html)
        text = re.sub(r"(?s)<!--.*?-->", "", text)
        # Replace line-breaking HTML elements with newlines
        text = re.sub(r"(?i)<br\s*/?>", "\n", text)
        text = re.sub(r"(?i)</?(p|div|h[1-6]|tr|li|pre|blockquote)[^>]*>", "\n", text)
        # Strip all other HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Decode HTML entities (&quot;, &lt;, &gt;, &amp;, &#39;, &nbsp;, etc.)
        text = html.unescape(text)

        if preserve_newlines:
            lines = [line.strip() for line in text.splitlines()]
            # Collapse multiple empty lines to single newline
            cleaned_lines = []
            prev_empty = False
            for line in lines:
                if line:
                    cleaned_lines.append(line)
                    prev_empty = False
                elif not prev_empty and cleaned_lines:
                    cleaned_lines.append("")
                    prev_empty = True
            return "\n".join(cleaned_lines).strip()
        else:
            return " ".join(text.split()).strip()

    @classmethod
    def _extract_title(cls, html_text: str, page: Optional[Any] = None) -> str:
        """Extracts problem title using CSS selectors and fallback regex."""
        # Check explicit class .problem-title
        m = re.search(r'class=["\'][^"\']*problem-title[^"\']*["\'][^>]*>(.*?)<', html_text, re.IGNORECASE | re.DOTALL)
        if m:
            clean = cls._clean_text(m.group(1))
            if clean:
                return clean

        # Check <h1> tags
        m = re.search(r'<h1[^>]*>(.*?)</h1>', html_text, re.IGNORECASE | re.DOTALL)
        if m:
            clean = cls._clean_text(m.group(1))
            if clean:
                return clean

        # Check numbered title in sanitized text before Problem Statement (Qwik SSR layout)
        clean_full = cls._clean_text(html_text, preserve_newlines=True)
        m_num = re.search(r'(?:^|\n)(\d+\.\s*[^\n]+?)(?=\n+(?:\d+\n+)?(?:Easy|Medium|Hard|Topics|Problem\s*Statement))', clean_full, re.IGNORECASE)
        if m_num:
            return m_num.group(1).strip()

        # Check <title> tag (e.g., "Odd or Even Sum - CodeKata - GUVI")
        m = re.search(r'<title>(.*?)</title>', html_text, re.IGNORECASE | re.DOTALL)
        if m:
            title_tag = cls._clean_text(m.group(1))
            # Strip suffixes like "- CodeKata - GUVI" or "- GUVI"
            title_tag = re.sub(r"(?i)\s*-\s*CodeKata\s*-\s*GUVI.*$", "", title_tag)
            title_tag = re.sub(r"(?i)\s*-\s*GUVI.*$", "", title_tag)
            if title_tag and title_tag.lower() not in ("sign in", "hcl guvi | learn to code in your native language") and "learn to code" not in title_tag.lower():
                return title_tag.strip()

        return "Unknown"

    @classmethod
    def _extract_category(cls, html_text: str, page: Optional[Any] = None) -> str:
        """Extracts category, topic, or difficulty level."""
        # Check .question-status
        m = re.search(r'class=["\'][^"\']*question-status[^"\']*["\'][^>]*>(.*?)<', html_text, re.IGNORECASE | re.DOTALL)
        if m:
            val = cls._clean_text(m.group(1))
            if val and val.lower() not in ("unsolved", "solved", "solved!"):
                return val

        # Check filter topic tab
        m = re.search(r'class=["\'][^"\']*filter-topics-tab-active[^"\']*["\'][^>]*>(.*?)<', html_text, re.IGNORECASE | re.DOTALL)
        if m:
            val = cls._clean_text(m.group(1))
            if val:
                return val

        # Check standard difficulty terms
        for diff in ("Easy", "Medium", "Hard"):
            if re.search(rf'\b{diff}\b', html_text, re.IGNORECASE):
                return diff

        return "General"

    @classmethod
    def _extract_description(cls, html_text: str) -> str:
        """Extracts the main problem prompt/description."""
        # Strategy 1: Explicit CSS class .problem-statement
        m = re.search(r'class=["\'][^"\']*problem-statement[^"\']*["\'][^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)
        if m:
            return cls._clean_text(m.group(1))

        # Strategy 2: Labeled heading block in text
        text = cls._clean_text(html_text, preserve_newlines=True)
        m = re.search(
            r'(?:Problem\s*Statement|Description|Problem\s*Description)\s*[:\-]?\s*(.*?)(?=(?:Input\s*(?:Description|Specification)|Constraints|Sample\s*Input|Output\s*(?:Description|Specification)|$))',
            text,
            re.IGNORECASE | re.DOTALL
        )
        if m:
            return m.group(1).strip()

        return ""

    @classmethod
    def _extract_input_spec(cls, html_text: str) -> str:
        """Extracts input specification/description."""
        # Strategy 1: Explicit CSS class .input-description
        m = re.search(r'class=["\'][^"\']*input-description[^"\']*["\'][^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)
        if m:
            return cls._clean_text(m.group(1))

        # Strategy 2: Labeled heading block in text
        text = cls._clean_text(html_text, preserve_newlines=True)
        m = re.search(
            r'(?:Input\s*(?:Description|Specification|Format)|Input)\s*[:\-]?\s*(.*?)(?=(?:Output\s*(?:Description|Specification|Format)|Output|Constraints|Sample\s*Input|$))',
            text,
            re.IGNORECASE | re.DOTALL
        )
        if m:
            return m.group(1).strip()

        return ""

    @classmethod
    def _extract_output_spec(cls, html_text: str) -> str:
        """Extracts output specification/description."""
        # Strategy 1: Explicit CSS class .output-description
        m = re.search(r'class=["\'][^"\']*output-description[^"\']*["\'][^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)
        if m:
            return cls._clean_text(m.group(1))

        # Strategy 2: Labeled heading block in text
        text = cls._clean_text(html_text, preserve_newlines=True)
        m = re.search(
            r'(?:Output\s*(?:Description|Specification|Format)|Output)\s*[:\-]?\s*(.*?)(?=(?:Sample\s*Input|Constraints|Explanation|$))',
            text,
            re.IGNORECASE | re.DOTALL
        )
        if m:
            return m.group(1).strip()

        return ""

    @classmethod
    def _extract_constraints(cls, html_text: str) -> str:
        """Extracts constraints block."""
        # Strategy 1: Explicit CSS class .constraints
        m = re.search(r'class=["\'][^"\']*constraints[^"\']*["\'][^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)
        if m:
            return cls._clean_text(m.group(1))

        # Strategy 2: Labeled heading block in text
        text = cls._clean_text(html_text, preserve_newlines=True)
        m = re.search(
            r'(?:Constraints?)\s*[:\-]?\s*(.*?)(?=(?:Sample\s*Input|Input|Output|Explanation|$))',
            text,
            re.IGNORECASE | re.DOTALL
        )
        if m:
            return m.group(1).strip()

        return ""

    @classmethod
    def _extract_sample_cases(cls, html_text: str) -> List[SampleCase]:
        """
        Extracts all sample test cases (input & expected output pairs).
        Supports:
          - Paired .sample-input and .sample-output CSS blocks
          - Numbered or unnumbered text blocks ("Sample Input 1:", "Sample Output 1:")
          - Fallback single sample extraction
        """
        cases: List[SampleCase] = []

        # Strategy 1: DOM Class Selectors (.sample-input and .sample-output)
        inputs_m = re.findall(r'class=["\'][^"\']*sample-input[^"\']*["\'][^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)
        outputs_m = re.findall(r'class=["\'][^"\']*sample-output[^"\']*["\'][^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)

        if inputs_m and outputs_m:
            for idx, (in_raw, out_raw) in enumerate(zip(inputs_m, outputs_m), start=1):
                clean_in = cls._clean_text(in_raw, preserve_newlines=True)
                clean_out = cls._clean_text(out_raw, preserve_newlines=True)
                cases.append(SampleCase(
                    input_text=clean_in,
                    expected_output=clean_out,
                    case_number=idx,
                ))
            return cases

        # If only inputs exist without outputs
        if inputs_m and not outputs_m:
            for idx, in_raw in enumerate(inputs_m, start=1):
                clean_in = cls._clean_text(in_raw, preserve_newlines=True)
                cases.append(SampleCase(
                    input_text=clean_in,
                    expected_output="",
                    case_number=idx,
                ))
            return cases

        # Strategy 2: Labeled Text Pattern Matching across sanitized text
        text = cls._clean_text(html_text, preserve_newlines=True)
        # Truncate any trailing Code Editor / Console / Footer blocks before matching Sample Input/Output
        text_for_samples = re.split(
            r"\n\s*(?:Accepted\b|Acceptance\s+Rate\b|Code\s+Editor\b|Are\s+you\s+sure\s+you\s+want\s+to\s+reset)",
            text,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        sample_pattern = re.compile(
            r"(?:^|\n)\s*(?:(?:Sample\s+Input)|(?:Input(?!\s*(?:Description|Specification|Format|Size))))\s*(?:Case\s*)?(?P<num>\d+)?\s*[:\-]?\s*\n?"
            r"(?P<input>.*?)\s*"
            r"(?:^|\n)\s*(?:(?:Sample\s+Output)|(?:Output(?!\s*(?:Description|Specification|Format))))\s*(?:Case\s*)?(?P=num)?\s*[:\-]?\s*\n?"
            r"(?P<output>.*?)\s*"
            r"(?:(?:\n\s*|\A)(?:Sample\s+)?Explanation\s*(?:Case\s*)?(?:\d+)?\s*[:\-]?\s*(?P<explanation>.*?))?"
            r"(?=(?:\n\s*(?:Sample\s+)?Input(?!\s*(?:Description|Specification|Format|Size))\s*(?:Case\s*)?\d*\s*[:\-])|(?:\n\s*Constraints)|(?:\n\s*Accepted\b)|(?:\n\s*Topics\b)|(?:\n\s*Code\s+Editor)|$)",
            re.DOTALL | re.IGNORECASE
        )

        matches = list(sample_pattern.finditer(text_for_samples))
        if matches:
            for idx, m in enumerate(matches, start=1):
                inp = m.group("input").strip()
                out = m.group("output").strip()
                exp = m.group("explanation").strip() if m.group("explanation") else None
                cases.append(SampleCase(
                    input_text=inp,
                    expected_output=out,
                    case_number=idx,
                    explanation=exp,
                ))
            return cases

        return cases


# Module-level convenience function fulfilling PROJECT.md contract
def extract_problem_spec(source: Any) -> ProblemSpecification:
    """
    Extract problem specification from Playwright Page or HTML string.
    Entry point matching PROJECT.md interface contract:
      extract_problem_spec(page: Page) -> ProblemSpec
    """
    return ProblemExtractor.extract(source)
