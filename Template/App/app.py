# Configure logging with debug level enabled
import logging
from flask import Flask, render_template, request, jsonify
import plotly.graph_objects as go
import numpy as np
import math

# Configure logging with debug level enabled
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Solvent database (HSP values)
SOLVENTS = {
    "Water": {"d":15.5, "p": 16.0, "h": 42.3},
    "Ethanol": {"d": 15.8, "p": 8.8, "h": 19.4},
    "Acetone": {"d": 15.5, "p": 10.4, "h": 7.0},
    "Toluene": {"d": 18.0, "p": 1.4, "h": 2.0},
    "Hexane": {"d": 14.9, "p": 0.0, "h": 0.0},
    "MTBE": {"d": 15.3, "p": 4.0, "h": 2.6},
    "Ethyl acetate": {"d": 15.8, "p": 5.3, "h": 7.2},
    "Methyl Isobutyl Ketone (MIBK)": {"d": 15.3, "p": 6.1, "h": 4.1},
    "Heptane": {"d": 15.3, "p": 0.0, "h": 0.0},
    "Rapeseed oil": {"d": 17.0, "p": 2.0, "h": 5.0},
    "Dimethyl sulfoxide (DMSO)": {"d": 18.4, "p": 16.4, "h": 10.2},
    "Propylene carbonate": {"d": 20.0, "p": 18.0, "h": 4.1},
    "N-Methyl-2-pyrrolidone (NMP)": {"d": 18.0, "p": 12.3, "h": 7.2},
    "γ-Butyrolactone (GBL)": {"d": 19.0, "p": 16.6, "h": 7.4},
    "Chloroform": {"d": 17.8, "p": 3.1, "h": 5.7},
    "Acetonitrile": {"d": 15.3, "p": 18.0, "h": 6.1},
    "Dichloromethane (DCM)": {"d": 18.2, "p": 6.3, "h": 7.1},
    "Anisole": {"d": 17.8, "p": 4.4, "h": 6.9},
    "Cyclohexanone": {"d": 17.8, "p": 8.4, "h": 5.1},
    "Tetrahydrofuran": {"d": 16.8, "p": 5.7, "h": 8.0},
    "Acetaldehyde" : {"d": 14.7, "p": 12.5, "h":7.9},
    "Acetic acid" : {"d": 14.5, "p": 8.0, "h":13.5},
    "Acetic Anhydride" : {"d": 16.0, "p": 11.7, "h":10.2},
   "Acetophenone" : {"d": 18.8, "p": 9.0, "h":4.0},
   "Acrylonitrile" : {"d": 16.0, "p": 12.8, "h":6.8},
   "AllyAlcohol" : {"d": 16.2, "p": 10.8, "h":16.8},
   "Amyl Acetate" : {"d": 15.8, "p": 3.3, "h":6.1},
   "Aniline" : {"d": 20.1, "p": 5.8, "h":11.2},
   "Benzaldehyde" : {"d": 19.4, "p": 7.4, "h":5.3},
   "Benzene" : {"d": 18.4, "p": 0, "h":2.0},
   "Benzoic acid" : {"d": 20.0, "p": 6.9, "h":10.8},
  "Benzonitrile" : {"d": 18.8, "p": 12.0, "h":3.3},
  "Benzophenone" : {"d": 19.5, "p": 7.2, "h":5.1},
  "Benzylalcohol" : {"d": 18.4, "p": 6.3, "h":13.7},
  "Benzyl Benzoate" : {"d": 20.0, "p": 5.1, "h":5.2},
  "Benzyl Butyl Phthalate" : {"d": 19.0, "p": 11.2, "h":3.1},
  "Benzyl Chloride" : {"d": 18.8, "p": 7.1, "h":2.6},
  "Biphenyl" : {"d": 19.7, "p": 1.0, "h":2.0},
"Bis-(M-phenoxyphenyl) Esther" : {"d": 19.6, "p": 3.1, "h":5.1},
    "Bromobezene": {"d": 19.2, "p": 5.5, "h": 4.1},
    "Bromochloromethane": {"d": 17.3, "p": 5.7, "h": 3.5},
    "Bromoform": {"d": 20.0, "p": 5.0, "h": 7.0},
    "1-Bromonapthelene": {"d": 20.6, "p": 3.1, "h": 4.1},
    "Bromotrifluoromethane (Freon 1381)": {"d": 14.3, "p": 2.4, "h": 0},
    "Butane": {"d": 14.1, "p": 0, "h": 0},
    "1,3 Butandiol": {"d": 16.5, "p": 8.1, "h": 20.9},
"1,4 Butandiol": {"d": 16.6, "p": 11.0, "h": 20.9},
"1-Butanol": {"d": 16.0, "p": 5.7, "h": 15.8},
"2-Butanol": {"d": 15.8, "p": 5.7, "h": 14.5},
"n-Butyl Acetate": {"d": 15.0, "p": 3.7, "h": 6.3},
"t-butyl Acetate": {"d": 15.0, "p": 3.7, "h": 6.0},
"n-Butyl Aceto Acetate": {"d": 16.6, "p": 5.8, "h": 7.3},
"n-Butyl Acrylate": {"d": 15.6, "p": 6.2, "h": 4.9},
"t-Buytl Alcohol": {"d": 15.2, "p": 5.1, "h": 14.7},
"n-Butyl Amine": {"d": 16.2, "p": 4.5, "h": 8.0},
"n-Butyl Amine/Acetic Acid": {"d": 16.0, "p": 20.3, "h": 18.4},
"Butyl Lactate": {"d": 15.8, "p": 6.5, "h": 10.2},
"Butyraldehyde": {"d": 15.6, "p": 10.1, "h": 6.2},
"Butyric Acid": {"d": 15.7, "p": 4.8, "h": 12.0},
"y-Butyrolactone (GBL)": {"d": 18.0, "p": 16.6, "h": 7.4},
"Butyronitrile": {"d": 15.3, "p": 12.4, "h": 5.1},
"Caprolactone (Epsilon)": {"d": 18.0, "p": 15.0, "h": 7.4},
"Carbon Disulfide": {"d": 20.2, "p": 0.0, "h": 0.6},
"Carbon Tetrachloride": {"d": 16.1, "p": 8.3, "h": 0},
"1-Chloro pentane": {"d": 16.0, "p": 6.9, "h": 1.9},
"3-Chloro-1-Propanol": {"d": 17.5, "p": 5.7, "h": 14.7},
"Chlorobezene": {"d": 19.0, "p": 4.3, "h": 2.0},
"1-Chlorobutane": {"d": 16.2, "p": 5.5, "h": 2.0},
"Chlorodifluoromethane (Freon 22)": {"d": 12.3, "p": 6.3, "h": 5.7},
"Cis-Decahydronapthalene": {"d": 17.6, "p": 0, "h": 0},
"m-Cresol": {"d": 18.5, "p": 6.5, "h": 13.7},
"Cyclohexane": {"d": 16.8, "p": 0, "h": 0.2},
"Cyclohexanol": {"d": 17.4, "p": 4.1, "h": 13.5},
"Cyclohexylamine": {"d": 17.2, "p": 3.1, "h": 6.5},
"Cyclohexylchloride": {"d": 17.3, "p": 5.5, "h": 2.0},
"Cyclopentanone": {"d": 17.9, "p": 11.9, "h": 5.2},
"Decane": {"d": 15.7, "p": 0, "h": 0},
"1-Decanol": {"d": 16.0, "p": 4.7, "h": 10.5},
"Di-(2-chloro-isopropyl) Ether": {"d": 19.0, "p": 8.2, "h": 5.1},
"Di-(2-Methoxyethyl) Ether": {"d": 15.7, "p":6.1, "h":6.5},
"Diacetone Alcohol": {"d": 15.8, "p": 8.2, "h": 10.8},
"Dibenzyl Ether": {"d": 19.6, "p": 3.4, "h": 5.2},
"Dibutyl Phthalate": {"d": 17.8, "p":8.6, "h": 4.1},
"Dibutyl Sebacate": {"d": 16.7, "p": 4.5, "h": 4.1},
"m-Dichlorobenzene": {"d": 19.2, "p": 5.1, "h": 2.7},
"0-Dichlorobenzene": {"d": 19.2, "p": 6.3, "h": 3.3},
"p-Dichlorobenzene": {"d": 19.7, "p": 5.6, "h": 2.7},
"1,4-Dichlorobutane": {"d": 18.3, "p": 7.7, "h": 2.8},
"Dichlorodifluoromethane (Freon 12)": {"d": 14.9, "p": 2.0, "h": 0},
"1,1-Dichloroethane": {"d": 16.5, "p": 7.8, "h": 3.0},
"1,2-Dichloroethylene": {"d": 17.0, "p": 8.0, "h": 3.2},
"Dichloroethylene": {"d": 16.7, "p": 7.8, "h": 3.3},
"Dichloromethane": {"d": 18.2, "p": 6.3, "h": 6.1},
"Dichloromonofluorimethane (Freon 21)": {"d": 15.8, "p": 3.1, "h": 5.7},
"1,2-Dichlorotetrafluoroethane (Freon 114)": {"d": 12.6, "p": 1.8, "h": 0},
"Diethanolamine": {"d": 17.2, "p": 7.0, "h": 19.0},
"Diethyl Amine": {"d": 14.9, "p": 2.3, "h": 6.1},
"1,2-Diethyl Benzene": {"d": 17.7, "p": 0.1, "h": 1.0},
"p-Diethyl Benzene": {"d": 18.0, "p": 0.0, "h": 0.6},
"Diethyl Carbonate": {"d": 15.1, "p": 6.3, "h": 3.5},
"Diethyl Ether": {"d": 14.5, "p": 2.9, "h": 4.6},
"Diethyl Ketone": {"d": 15.8, "p": 7.6, "h": 4.7},
"Diethyl Phthalate": {"d": 17.6, "p": 9.6, "h": 4.5},
"Diethyl Sulfate": {"d": 15.7, "p": 12.7, "h": 5.1},
"Diethyl Sulfide": {"d": 16.8, "p": 3.1, "h": 2.0},
"2-(Diethylamino) Ethanol": {"d": 15.7, "p": 5.8, "h": 12.0},
"Diethylene Glycol": {"d": 16.6, "p": 12.0, "h": 19.0},
"Diethylene Glycol Butyl Ether Acetate": {"d": 16.0, "p": 4.1, "h": 8.2},
"Diethylene Glycol Hexyl Ether": {"d": 16.0, "p": 6.0, "h": 10.0},
"Diethylene Glycol Monobutyl Ether": {"d": 16.0, "p": 7.0, "h": 10.6},
"Diethylene Glycol Monoethyl Ether": {"d": 16.1, "p": 9.2, "h": 12.2},
"Diethylene Glycol Monoethyl Ether Acetae": {"d": 16.2, "p":5.1, "h": 9.2},
"Diethylene Glycol Monomethyl Ether": {"d": 16.2, "p": 7.8, "h": 12.6},
"Diethylenetriamine": {"d": 16.7, "p": 7.1, "h": 14.3},
"Di-isobutyl Carbinol": {"d": 14.9, "p": 3.1, "h": 10.8},
"Di-isobutyl Ketone": {"d": 16.0, "p": 3.7, "h": 4.1},
"Di-isopropylamine": {"d": 14.8, "p": 1.7, "h": 3.5},
"1,2-Dimethoxybenzene": {"d": 19.2, "p": 4.4, "h": 9.4},
"Dimethyl Disulfide": {"d": 17.6, "p": 7.8, "h": 6.5},
"Dimethyl Formanide (DMF)": {"d": 17.4, "p": 13.7, "h": 11.3},
"1,1-Dimethyl Hydrazine": {"d": 15.3, "p": 5.9, "h": 11.0},
"Dimethyl Phthalate": {"d": 18.6, "p": 10.8, "h": 4.9},
"Dimethyl Sulfone": {"d": 19.0, "p": 19.4, "h": 12.3},
"1,4-Dioxane": {"d": 17.5, "p": 1.8, "h": 9.0},
"Dipropylene Glycol": {"d": 16.5, "p": 10.6, "h": 17.7},
"Dipropylene Glycol Methyl Ether": {"d": 15.5, "p": 5.7, "h": 11.2},
"Dodecane": {"d": 16.0, "p": 0, "h": 0},
"Eicosane": {"d": 16.5, "p": 0, "h": 0},
"Epichlorohydrin": {"d": 17.5, "p": 7.6, "h": 7.6},
"Ethanethiol": {"d": 15.7, "p": 6.5, "h": 7.1},
"Ethanolamine": {"d": 17.0, "p": 15.5, "h": 21.0},
"Ethyl Acrylate": {"d": 15.5, "p": 7.1, "h": 5.5},
"Ethyl Amyl Ketone": {"d": 16.2, "p": 4.5, "h": 4.1},
"Ethyl Benzene": {"d": 17.8, "p": 0.6, "h": 1.4},
"Ethyl Bromide": {"d": 16.5, "p": 8.4, "h": 2.3},
"Ethyl Butyl Ketone": {"d": 16.2, "p": 5.0, "h": 4.1},
"Ethyl Chloride": {"d": 15.7, "p": 6.1, "h": 2.9},
"Ethyl Chloroformate": {"d": 16.4, "p": 11.0, "h": 8.0},
"Ethyl Cinnamate": {"d": 18.4, "p": 8.2, "h": 4.1},
"Ethyl Formate": {"d": 15.5, "p": 8.4, "h": 8.4},
"Ethyl Lactate": {"d": 16.0, "p": 7.6, "h": 12.5},
"Ethylene Carbonate": {"d": 18.0, "p": 21.7, "h": 5.1},
"Ethylene Cyanohydrin": {"d": 17.2, "p": 18.8,"h": 17.6},
"Ethylene Dibromide": {"d": 19.2, "p": 3.5, "h": 8.6},
"Ethylene Dichloride": {"d": 18.0, "p": 7.4, "h": 4.1},
"Ethylene Glycol": {"d": 17.0, "p": 11.0, "h": 26.0},
"Ethylene Glycol Butyl Ether Acetate": {"d": 15.3, "p": 7.5, "h": 6.8},
"Ethylene Glycol dibutyl Ether": {"d": 15.7, "p": 4.5, "h": 4.2},
"Ethylene Glycol monobutyl Ether": {"d": 16.0, "p": 5.1, "h": 12.3},
"Ethylene Glycol monoethyl Ether": {"d": 15.9, "p": 7.2, "h": 14.0},
"Ethylene Glycol monoethyl Ether Acetate": {"d": 15.9, "p": 4.7, "h": 10.6},
"Ethylene Glycol monoethyl Ether ": {"d": 16.0, "p": 8.2, "h": 15.0},
"Ethylene Glycol monoethyl Ether Acetate ": {"d": 15.9, "p": 5.5, "h": 11.6},
"Ethylenediamine ": {"d": 16.6, "p": 8.8, "h": 17.0},
"Formamide": {"d": 17.2, "p": 26.2, "h": 19.0},
"Formic Acid": {"d": 14.6, "p": 10.0, "h": 14.0},
"Furan": {"d": 17.0, "p": 1.8, "h": 5.3},
"Furfural": {"d": 18.6, "p": 14.9, "h": 5.1},
"Furfuryl Alcohol": {"d": 17.4, "p": 7.6, "h": 15.1},
"Glycerol": {"d": 17.4, "p": 11.3, "h": 27.2},
"Hexadecane": {"d": 16.3, "p": 0, "h": 0},
"Hexamethylphosphoramide": {"d": 18.5, "p": 11.6, "h":8.7},
"Hexyl Acetate": {"d": 15.8, "p": 2.9, "h": 5.9},
"Isoamyl Acetate": {"d": 15.3, "p": 3.1, "h": 7.0},
"Isobutyl Acetate": {"d": 15.1, "p": 3.7, "h": 6.3},
"Isobutyl Alcohol": {"d": 14.4, "p": 7.3, "h": 12.9},
"Isopentane": {"d": 13.8, "p": 0, "h": 0},
"Isophorone": {"d": 17.0, "p": 8.0, "h": 5.0},
"Isopropyl Acetate": {"d": 14.9, "p": 4.5, "h": 8.2},
"Isopropyl Palmitate": {"d": 16.2, "p": 3.9, "h": 3.7},
"Mesityl Oxide": {"d": 16.4, "p": 7.2, "h": 5.0},
"Mesitylene": {"d": 18.0, "p": 0.6, "h": 0.6},
"Methacrylonitrile": {"d": 15.8, "p": 9.5, "h": 5.4},
"Methanol": {"d": 14.7, "p": 12.3, "h": 22.3},
"2-Methoxy-2-methylpropane": {"d": 14.8, "p": 4.3, "h": 5.0},
"o-Methoxyphenol": {"d": 18.0, "p": 7.0, "h": 12.0},
"Methyl Acetate": {"d": 15.5, "p": 7.2, "h": 7.6},
"Methyl Acrylate": {"d": 15.3, "p":6.7, "h": 9.4},
"Methyl Amyl Acetate": {"d": 15.2, "p": 3.1, "h": 6.8},
"Methyl Benzoate": {"d": 18.9, "p": 8.2, "h": 4.7},
"Methyl Butyl Ketone": {"d": 15.3, "p": 6.1, "h": 4.1},
"Methyl Chloride": {"d": 15.3, "p": 9.9, "h": 3.9},
"Methyl Cyclohexane": {"d": 16.0, "p": 0, "h": 1.0},
"Methyl Ethyl Ketone": {"d": 16.0, "p": 9.0, "h": 5.1},
"Methyl Isoamyl Ketone": {"d": 16.0, "p": 5.7, "h": 4.1},
"Methyl Isobutyl Carbinol": {"d": 15.4, "p": 3.3, "h": 12.3},
"Methyl Methacrylate": {"d": 15.8, "p": 6.5, "h": 5.4},
"1-Methyl Napthalene": {"d": 19.7, "p": 0.8, "h": 4.7},
"Methyl Oleate": {"d": 16.2, "p": 3.8, "h": 4.5},
"N-Methyl Pyrrolidine": {"d": 16.8, "p": 2.8, "h": 6.7},
"Methyl Salicylate": {"d": 18.1, "p": 8.0, "h": 13.9},
"Methylal": {"d": 15.0, "p": 1.8, "h": 8.6},
"Methylene Dichloride": {"d": 17.0, "p": 7.3, "h": 7.1},
"Methylene Diiodide": {"d": 22.0, "p": 3.9, "h": 5.5},
"Morpholine": {"d": 18.0, "p": 4.9, "h": 11.0},
"N,N-Dimethyl Acetamide": {"d": 16.8, "p": 11.5, "h": 9.4},
"Naptha High-Flash": {"d": 17.9, "p": 0.7, "h": 1.8},
"Napthalene": {"d": 19.2, "p": 2.0, "h": 5.9},
"Nitrobenzene": {"d": 20.0, "p": 10.6, "h": 3.1},
"Nitroethane": {"d": 16.0, "p": 15.5, "h": 4.5},
"Nitromethane": {"d": 15.8, "p": 18.8, "h": 6.1},
"1-Nitropane": {"d": 16.6, "p": 12.3, "h": 5.5},
"2-Nitropane": {"d": 16.2, "p": 12.1, "h": 4.1},
"Nonane": {"d": 15.7, "p": 0, "h": 0},
"Nonyl Phenol": {"d": 16.5, "p": 4.1, "h":9.2},
"Nonyl Phenoxy Ethanol": {"d": 16.7, "p": 10.2, "h": 8.4},
"Octane": {"d": 15.5, "p": 0, "h": 0},
"Octanoic Acid": {"d": 15.7, "p": 3.3, "h": 8.2},
"2-Octanol": {"d": 16.1, "p": 4.9, "h": 11.0},
"1-Octanol": {"d": 16.0, "p": 5.0, "h": 11.2},
"Oleic Acid": {"d": 16.0, "p": 2.8, "h": 6.2},
"Oleyl Alchohol": {"d": 16.5, "p": 2.6, "h": 8.0},
"1,3-Pentadiene": {"d": 15.0, "p": 2.5, "h": 4.0},
"Pentane": {"d": 14.5, "p": 0, "h": 0},
"2-Pentanol": {"d": 15.6, "p": 6.4, "h": 13.3},
"1-Pentanol": {"d": 15.9, "p":5.9, "h": 13.9},
"Perfluro Dimethylcyclohexane": {"d": 12.4, "p": 0, "h": 0},
"Perfluroheptane": {"d": 12.0, "p": 0, "h": 0},
"Perfluoromethylcyclohexane": {"d": 12.4, "p": 0, "h": 0},
"Phenol": {"d": 18.5, "p": 5.9, "h": 14.9},
"1-Propanol": {"d": 16.0, "p": 6.8, "h": 17.4},
"2-Propanol": {"d": 15.8, "p": 6.1, "h": 16.4},
"Propionitrile": {"d": 15.3, "p": 14.3, "h": 5.5},
"n-Propyl Acetate": {"d": 16.0, "p": 6.8, "h": 17.4},
"Propyl Amine": {"d": 16.0, "p": 4.9, "h": 8.6},
"Propyl Chloride": {"d": 16.0, "p": 7.8, "h": 2.0},
"Propylene Carbonate": {"d": 20.0, "p": 18.0, "h": 4.1},
"Propylene Glycol": {"d": 16.8, "p": 10.4, "h": 21.3},
"Propylene Glycol Monobutyl Ether": {"d": 15.3, "p": 4.5, "h": 9.2},
"Propylene Glycol Monoethyl Ether": {"d": 15.7, "p": 6.5, "h": 10.5},
"Propylene Glycol Monoisobutyl Ether": {"d": 15.1, "p": 4.7, "h": 9.8},
"Propylene Glycol monomethyl Ether": {"d": 15.6, "p": 6.3, "h": 11.6},
"Propylene Glycol monophenyl Ether": {"d": 17.4, "p": 5.3, "h": 11.5},
"Propylene Glycol Monopropyl Ether": {"d": 15.8, "p": 7.0, "h": 9.2},
"Pyridine": {"d": 19.0, "p": 8.8, "h": 5.9},
"Pyrrolidine": {"d": 17.9, "p": 6.5, "h": 7.4},
"Quinoline": {"d": 20.5, "p": 5.6, "h": 5.7},
"Salicyaldehyde": {"d": 19.0, "p": 10.5, "h": 12.0},
"Styrene": {"d": 18.6, "p": 1.0, "h": 4.1},
"Succinic Anhydride": {"d": 18.6, "p": 17.5, "h": 16.0},
"1,1,2,2- Tetrabromoethane": {"d": 21.0, "p": 7.0, "h": 8.2},
"1,1,2,2- Tetrachloroethane": {"d": 18.0, "p": 4.4, "h": 4.2},
"Tetrachloroethylene": {"d": 18.3, "p": 5.7, "h": 0},
"Tetraethylorthosilicate": {"d": 13.9, "p": 4.3, "h": 0.6},
"Tetrahydrofuran (THF)": {"d": 16.8, "p": 5.7, "h": 8.0},
"Tetrahydronapthalene": {"d": 19.6, "p": 2.0, "h": 2.9},
"1,2,3,4-Tetramethylbenzene": {"d": 18.8, "p": 0.5, "h": 0.5},
"1,2,3,5-Tetramethylbenzene": {"d": 18.6, "p": 0.5, "h": 0.5},
"Tetramethyurea": {"d": 16.7, "p": 8.2, "h": 11.0},
"2-Toluidine": {"d": 19.4, "p": 5.8, "h": 9.4},
"Trichlorobiphenyl": {"d": 19.2, "p": 5.3, "h": 4.1},
"1,1,1-Trichloroethane": {"d": 16.8, "p": 4.3, "h": 2.0},
"1,1,2-Trichloroethane": {"d": 18.2, "p": 5.3, "h": 6.8},
"Trichloroethylene": {"d": 18.0, "p": 3.1, "h": 5.3},
"Trichlorofluoromethane (Freon 11)": {"d": 15.3, "p": 2.0, "h": 0},
"1,1,2-Trichlorotrifluoroethane (Freon 113)": {"d": 14.7, "p": 1.6, "h": 0},
"Tricresyl Phosphate": {"d": 19.0, "p": 12.3, "h": 4.5},
"Tricresyl Alcohol": {"d": 16.2, "p": 3.1, "h": 9.0},
"Triethanolamine": {"d": 17.3, "p": 7.6, "h": 21.0},
"Triethylamine": {"d": 15.5, "p": 0.4, "h": 1.0},
"Triethylene Glycol": {"d": 16.0, "p": 12.5, "h": 18.6},
"Triethylene Glycol Monooleyl Ether": {"d": 16.0, "p": 3.1, "h": 8.4},
"Triethylphosphate": {"d": 16.7, "p": 11.4, "h": 9.2},
"Trifluoroacetic Acid": {"d": 15.6, "p": 9.7, "h": 11.4},
"Texanol": {"d": 15.1, "p": 6.1, "h": 9.8},
"Trimethylbezene": {"d": 18.0, "p": 1.0, "h": 1.0},
"2,2,4-Trimethylpentane": {"d": 14.1, "p": 0, "h": 0},
"Trimethylphosphate": {"d": 15.7, "p": 10.5, "h": 10.2},
"p-Xylene": {"d": 17.8, "p": 1.0, "h": 3.1},
"Acetic acid ethyl ester": {"d": 15.8, "p": 5.3, "h": 7.2},
"Trichloro-methane": {"d": 17.8, "p": 3.1, "h": 5.7},
   "Acetic acid ethyl ester": {"d": 15.8, "p": 5.3, "h": 7.2},
   "Trichloro-methane": {"d": 17.8, "p": 3.1, "h": 5.7},
    }

@app.route('/api/SOLVENTS')
def get_solvents():
    return jsonify(SOLVENTS)

def get_solutes():
    # Solute presets
    SOLUTES = {
        "Piceatannol": {"d": 22.7, "p": 7.11, "h": 26.36, "ro": 20.43},
        "Resveratrol": {"d": 23.1, "p": 6.1, "h": 20.5, "ro": 16.09},
        "Curcumin": {"d": 18.2, "p": 8.6, "h": 11.5, "ro": 5.5},
        "Quercetin": {"d": 21.3, "p": 9.4, "h": 14.2, "ro": 4.8},
        "Genistein": {"d": 19.0, "p": 8.0, "h": 11.8, "ro": 5.1},
        "Luteolin": {"d": 20.0, "p": 9.2, "h": 12.7, "ro": 5.0},
        "Pterostilbene": {"d": 19.2, "p": 6.9, "h": 9.8, "ro": 5.3},
        "Apigenin": {"d": 19.6, "p": 7.2, "h": 12.1, "ro": 5.2},  # Found in chamomile, parsley
        "Baicalein": {"d": 18.7, "p": 8.0, "h": 10.5, "ro": 5.3},  # Found in skullcap
        "Catechin": {"d": 21.0, "p": 9.1, "h": 14.5, "ro": 5.0},  # Found in tea, cocoa
        "Epicatechin": {"d": 20.8, "p": 8.9, "h": 13.9, "ro": 5.0},  # Found in green tea, cocoa
        "Hesperetin": {"d": 19.2, "p": 7.6, "h": 10.7, "ro": 5.1},  # Found in citrus fruits
        "Kaempferol": {"d": 20.2, "p": 9.0, "h": 13.2, "ro": 5.0},  # Found in broccoli, kale
        "Myricetin": {"d": 21.4, "p": 9.7, "h": 15.0, "ro": 4.9},  # Found in berries, tea
        "Naringenin": {"d": 19.0, "p": 7.5, "h": 11.0, "ro": 5.2},  # Found in citrus fruits
        "Rutin": {"d": 21.6, "p": 9.8, "h": 16.3, "ro": 4.8},  # Found in buckwheat, citrus fruits
        "Taxifolin": {"d": 20.7, "p": 8.8, "h": 13.7, "ro": 5.0},  # Found in milk thistle, onions
        "Triolein": {"d": 16.4, "p": 3.1, "h": 4.9, "ro": 6.2},
        "Polystyrene": {"d": 18.6, "p": 4.5, "h": 2.9, "ro": 10.6},
        "Polyethylene": {"d": 18.0, "p": 0.0, "h": 2.0, "ro": 9.8},
        "PVC": {"d": 18.2, "p": 7.5, "h": 8.3, "ro": 8.1},
        "PMMA": {"d": 18.6, "p": 10.5, "h": 7.5, "ro": 8.6},
        "Nylon-6,6": {"d": 18.6, "p": 5.6, "h": 12.8, "ro": 6.7},
        "PLA": {"d": 18.6, "p": 9.9, "h": 6.0, "ro": 8.4},
        "ABS": {"d": 17.6, "p": 8.6, "h": 4.7, "ro": 9.2},
        "PETG": {"d": 18.2, "p": 6.4, "h": 6.6, "ro": 8.8},
        "TPU": {"d": 17.5, "p": 9.3, "h": 8.5, "ro": 8.0},
        "Nylon (PA12)": {"d": 17.0, "p": 3.7, "h": 6.4, "ro": 8.2},
        "PEEK": {"d": 19.5, "p": 5.2, "h": 5.2, "ro": 10.8},
        "PVA": {"d": 15.6, "p": 18.8, "h": 16.9, "ro": 7.0},
        "HIPS": {"d": 18.0, "p": 4.3, "h": 2.7, "ro": 10.4},
        "ASA": {"d": 18.1, "p": 9.5, "h": 5.0, "ro": 9.0},
        "PC (Polycarbonate)": {"d": 19.1, "p": 7.5, "h": 6.0, "ro": 9.5},
        "Pullan": {"d": 18.7, "p": 18.1, "h": 23.5, "ro": 47.7},
    }
    return jsonify(SOLUTES)



@app.route('/')
def index():
  return render_template('index.html')
@app.route('/calculate', methods=['POST'])
def calculate_solubility():
    try:
        pass  # Add your code logic here
    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        data = request.get_json()

        # Get parameters from request
        solute = data.get('SOLUTE', {})
        solvent = data.get('SOLVENT', {})
        temperature = data.get('temperature', 25.0)
def calculate_distance(solute, solvent):
    """Calculate the Hansen solubility distance between solute and solvent."""
    try:
        distance = math.sqrt(
            4 * (solute["d"] - solvent["d"]) ** 2 +
            (solute["p"] - solvent["p"]) ** 2 +
            (solute["h"] - solvent["h"]) ** 2
        )
        logger.debug("Calculated distance (Ra): %s for solute %s and solvent %s", distance, solute, solvent)
        return distance
    except KeyError as e:
        raise ValueError(f"Missing HSP parameter: {e}")

        # Temperature correction (simplified)
        solubility = solubility * (1 + 0.02 * (temperature - 25))

        # Generate solubility vs temperature curve
        temp_range = np.linspace(0, 100, 101)
        solubility_values = []

        for temp in temp_range:
            temp_solubility = solubility * (1 + 0.02 * (temp - 25))
            solubility_values.append(max(0, temp_solubility))
        # Create graph data for frontend
        graph_data = {
            "x": temp_range.tolist(),
            "y": solubility_values,
            "current_temp": temperature,
            "current_solubility": solubility
        }


def create_3d_plot(plot_data, solute=None):
    logger.debug("Creating 3D plot with plot_data: %s and solute: %s", plot_data, solute)
    fig = go.Figure()

    # Add solvent points
    fig.add_trace(go.Scatter3d(
        x=plot_data["d_values"],
        y=plot_data["p_values"],
        z=plot_data["h_values"],
        mode="markers+text",
        marker=dict(
            size=10,
            color=plot_data["colors"], # colors represent solubility
            opacity=0.8,
            colorscale="Viridis",  # Or any other colorscale like 'RdYlBu'
            symbol="circle"
        ),
        text=plot_data["solvents"],
        hoverinfo="text",
        hovertext=[f"{name}: (δD={d:.1f}, δP={p:.1f}, δH={h:.1f})"
                   for name, d, p, h in zip(
                plot_data["solvents"],
                plot_data["d_values"],
                plot_data["p_values"],
                plot_data["h_values"]
            )],
        name="Solvents"
    ))

    # Add solute point and sphere (if provided)
    if solute:
        fig.add_trace(go.Scatter3d(
            x=[solute["d"]],
            y=[solute["p"]],
            z=[solute["h"]],
            mode="markers+text",
            marker=dict(
                size=14,
                color="blue",
                opacity=0.9,
                symbol="diamond"
            ),
            text=["Solute"],
            hoverinfo="text",
            hovertext=f"Solute: (δD={solute['d']:.1f}, δP={solute['p']:.1f}, δH={solute['h']:.1f})",
            name="Solute"
        ))

        if "ro" in solute:
            u, v = np.mgrid[0:2 * np.pi:20j, 0:np.pi:10j]
            radius = solute["ro"]
            x = radius * np.cos(u) * np.sin(v) + solute["d"]
            y = radius * np.sin(u) * np.sin(v) + solute["p"]
            z = radius * np.cos(v) + solute["h"]

            fig.add_trace(go.Surface(
                x=x, y=y, z=z,
                opacity=0.2,
                colorscale=[[0, 'blue'], [1, 'blue']],
                showscale=False,
                name="Solubility Sphere"
            ))


        scene=dict(
            xaxis_title="δD (Dispersion)",
            yaxis_title="δP (Polar)",
            zaxis_title="δH (Hydrogen Bonding)",
            aspectmode='cube',
            xaxis=dict(showgrid=True, gridwidth=2, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridwidth=2, gridcolor='lightgray'),
            zaxis=dict(showgrid=True, gridwidth=2, gridcolor='lightgray'),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        title="Hansen Solubility Parameters in 3D Space",
        margin=dict(l=0, r=0, b=0, t=30),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        height=600
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            title="Solubility Status",
            traceorder="normal",
            itemsizing="constant"
        )
    )
    # Hovertext should be defined outside the update_layout function
    hovertext = [f"{name}: (δD={d:.1f}, δP={p:.1f}, δH={h:.1f}) - {status}"
                 for name, d, p, h, status in zip(
            plot_data["solvents"],
            plot_data["d_values"],
            plot_data["p_values"],
            plot_data["h_values"],
            plot_data["colors"]
        )]

    fig_json = fig.to_json()
    logger.debug("Generated plot JSON: %s", fig_json)
    return fig_json


def get_solute_from_request(data):
    global SOLUTES  # Ensure SOLUTES is accessible within this function
    solute_name = data.get("solute_name")
    if solute_name and solute_name in SOLUTES:
        logger.debug("Using preset solute: %s", solute_name)
        return SOLUTES[solute_name]
    else:
        try:
            solute = {
                "d": float(data["solute_d"]),
                "p": float(data["solute_p"]),
                "h": float(data["solute_h"]),
                "ro": float(data["solute_ro"])
            }
            logger.debug("Using custom solute parameters: %s", solute)
            return solute
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid solute parameters: {str(e)}")


def get_solubility_status(red_value):
    # Adjusted thresholds: values equal to 1 are now considered "Soluble"
    if red_value <= 1:
        return "Soluble", "green"
    elif red_value <= 1.5:
        return "Partially Soluble", "orange"
    else:
        return "Insoluble", "red"


@app.route("/")
def index():
    logger.debug("Rendering index page")
    return render_template("index.html", solvents=sorted(SOLVENTS.keys()), solutes=SOLUTES)


@app.route("/api/search_solvents", methods=["GET"])
def search_solvents():
    query = request.args.get("q", "").lower()
    logger.debug("Search solvents query: '%s'", query)
    results = [{"name": name} for name in SOLVENTS if query in name.lower()]
    logger.debug("Search solvents results: %s", results)
    return jsonify(results)


@app.route("/api/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()
        logger.debug("Received calculation request: %s", data)
        if not data:
            return jsonify({"error": "No data provided"}), 400

        try:
            solute = get_solute_from_request(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        if solute["ro"] <= 0:
            return jsonify({"error": "Ro must be positive"}), 400

        selected_solvents = data.get("solvents", [])
        if not selected_solvents:
            return jsonify({"error": "No solvents selected"}), 400

        results = {}
        plot_data = {"solvents": [], "d_values": [], "p_values": [], "h_values": [], "colors": []}

        for solvent_name in selected_solvents:
            solvent = SOLVENTS.get(solvent_name)
            if not solvent:
                logger.warning("Solvent %s not found", solvent_name)
                continue

            ra = calculate_distance(solute, solvent)
            red = ra / solute["ro"]
            solubility, color = get_solubility_status(red)

            results[solvent_name] = {
                "d": solvent["d"],
                "p": solvent["p"],
                "h": solvent["h"],
                "ra": round(ra, 2),
                "red": round(red, 2),
                "solubility": solubility
            }

            plot_data["solvents"].append(solvent_name)
            plot_data["d_values"].append(solvent["d"])
            plot_data["p_values"].append(solvent["p"])
            plot_data["h_values"].append(solvent["h"])
            plot_data["colors"].append(color)

        plot_json = create_3d_plot(plot_data, solute)
        logger.debug("Calculation results: %s", results)

        return jsonify({"results": results, "plot_json": plot_json})

    except Exception as e:
        logger.error("Error in calculate: %s", str(e))
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)

