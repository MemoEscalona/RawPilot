import os
from pprint import pprint
from core.raw_loader import load_raw
from core.analyzer import analyze_image
from core.decision_engine import build_edit_decisions
from core.xmp_generator import generate_xmp
from utils.report_utils import (print_photo_summary, print_analysis_summary,print_decision_log, print_decision_summary)


def main():

    raw_file="/data/raws/IMG_4080.CR3"

    if not os.path.exists(raw_file):
        print("Archivo RAW no encontrado.")
        return
    
    print("\nCargando RAW...")
    img = load_raw(raw_file)
    print("\nDatos generales...")
    print_photo_summary(img.metadata)

    print("\nAnalizando imagen...")
    analysis = analyze_image(img.working_image)
    print_analysis_summary(analysis)

    print("Generando decisiones de edición...\n")
    decisions= build_edit_decisions(analysis)
    print_decision_summary(decisions)

    print("Generando XMP...\n")
    xmp_path = generate_xmp(raw_file, decisions["settings"])

    if xmp_path:
        print(f"XMP generado correctamente: {xmp_path}")
    else:
        print("Ya existe un archivo XMP. No se sobrescribió.")
if __name__ == "__main__":
    main()