# Telop From Image (Safe Bilingual)

Desktop application to infer telop (caption) styles from user images and export a `.mogrt` for After Effects. All processing occurs offline and no fonts or third-party assets are included.

## Features
- Analyze user-provided images to estimate caption styling.
- Edit and preview telop parameters.
- Generate ExtendScript to build a telop composition and export as `.mogrt`.
- Save and load styles as JSON.
- Strict bilingual disclaimer shown on every launch.

## Usage
```
python main.py
```

The disclaimer dialog will appear on each launch. Scroll to the end, acknowledge understanding, and click **Continue / 続行** to proceed.

## License
MIT License. See `LICENSE` and `NOTICE` for details. No fonts or third-party assets are included; users must supply their own fonts and ensure they have rights to use them.
