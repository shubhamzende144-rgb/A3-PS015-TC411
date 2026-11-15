class ProbeSpeakError(Exception):
    pass

class SafetyError(ProbeSpeakError):
    """A lab or simulated run tried to touch the real network."""
