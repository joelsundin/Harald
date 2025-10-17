def add_flashcard(ss, word, translation):
    if not ss.get("flashcards"):
        ss.flashcards = []
    ss.flashcards.append({
        "word": word,
        "translation": translation
    })
    print(f"Added flashcard: {word} -> {translation}")

add_flashcard_function = {
    "name": "add_flashcard",
    "description": "Adds a word to the user's flashcards for later review.",
    "parameters": {
        "type": "object",
        "properties": {
            "word": {
                "type": "string",
                "description": "The Swedish word to be added to flashcards.",
            },
            "translation": {
                "type": "string",
                "description": "The English translation of the Swedish word.",
            },
        },
        "required": ["word", "translation"],
    },
}