import string


class PromptTemplate:
    """Safely formats prompt templates with required-variable validation."""

    def __init__(self, template_str: str):
        self.template_str = template_str
        # Dynamically extract all required variables (like {crop} or {question}) from the string
        self.expected_vars = {
            fname for _, fname, _, _ in string.Formatter().parse(template_str) if fname
        }

    def format(self, **kwargs) -> str:
        """Validates inputs and returns the formatted prompt string."""
        # Check if the user forgot to pass a required variable
        missing_vars = self.expected_vars - kwargs.keys()
        if missing_vars:
            raise ValueError(f"CRITICAL ERROR: Missing required prompt variables: {missing_vars}")

        return self.template_str.format(**kwargs)


# ---------------------------------------------------------
# TEMPLATE 1: Role-Based Q&A (Persona Control)
# ---------------------------------------------------------
agronomist_template = PromptTemplate(
    "You are a highly experienced, overly technical, and impatient senior agronomist. "
    "A junior farmer is asking you a question about {crop}. "
    "Answer their question accurately using advanced botanical terminology, but sound annoyed that they are asking something so basic.\n\n"
    "Question: {question}"
)


# ---------------------------------------------------------
# TEMPLATE 2: Few-Shot Summarizer (Pattern Forcing)
# ---------------------------------------------------------
summarizer_template = PromptTemplate(
    "You are an AI that summarizes agricultural reports into EXACTLY three bullet points. Nothing more, nothing less.\n\n"
    "Example 1:\n"
    "Input: The field is showing signs of nitrogen deficiency. The lower leaves are turning yellow, and plant growth is stunted. We need to apply urea immediately.\n"
    "Output:\n"
    "- Nitrogen deficiency detected.\n"
    "- Symptoms include yellowing lower leaves and stunted growth.\n"
    "- Immediate application of urea is required.\n\n"
    "Example 2:\n"
    "Input: Late blight has been spotted in the northern potato sector. Lesions are appearing on the leaves, and white fungal growth is visible under high humidity.\n"
    "Output:\n"
    "- Late blight identified in northern potato sector.\n"
    "- Symptoms include leaf lesions and white fungal growth.\n"
    "- High humidity is exacerbating the condition.\n\n"
    "Now, summarize this input:\n"
    "Input: {text}\n"
    "Output:"
)


# ---------------------------------------------------------
# TEMPLATE 3: The JSON Classifier (System-to-System Output)
# ---------------------------------------------------------
json_classifier_template = PromptTemplate(
    "You are a strict data-parsing agricultural AI. Analyze the following symptom description and output a JSON object.\n"
    "You must output ONLY raw, valid JSON. \n"
    "Do NOT wrap the JSON in markdown formatting (e.g., ```json ). \n"
    "Do NOT include any introductory or concluding text.\n\n"
    "The JSON must have exactly these keys:\n"
    "- \"suspected_disease\" (string)\n"
    "- \"confidence_score\" (float between 0.0 and 1.0)\n"
    "- \"requires_quarantine\" (boolean)\n\n"
    "Symptom Description: {symptom_description}"
)
