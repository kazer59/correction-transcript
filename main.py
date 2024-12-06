#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import tkinter as tk
from gui import SpellCheckerGUI

def main():
    try:
        root = tk.Tk()
        app = SpellCheckerGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Une erreur est survenue : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
