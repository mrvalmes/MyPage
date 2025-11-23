#Libreria de gestion de datos
import pandas as pd
import cn as cn
from flask import jsonify



# Función para procesar los archivos.
def procesar_dataframe_ventas(file):
    try:
        if isinstance(file, pd.DataFrame):
            df = file
        else:
            df = pd.read_excel(file)  # Leer el archivo Excel
        print(df.head())  # Muestra las primeras filas para verificar la carga correcta
        # Diccionario para mapear condiciones y sus valores, para ajustar errores en grupos.        
        mapeo_condiciones_grupos = {
        "4G LTE OFICINA": "847 - GRUPO NET LTE 6",
        "4G LTE OFICINA - 10 Mbps / 2 Mbps": "847 - GRUPO NET LTE 6",
        "4G LTE OFICINA - 3 Mbps / 1.5 Mbps": "844 - GRUPO NET LTE 3",
        "ALTICE BUSINESS FIT": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "ALTICE BUSINESS FIT - ALTICE BUSINESS FIT 150": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "ALTICE BUSINESS FIT CERRADO": "829 - ACTIV-NEGOCIOS-GRUPO 4",
        "ALTICE BUSINESS FIT CERRADO - ALTICE BUSINESS FIT CERRADO": "829 - ACTIV-NEGOCIOS-GRUPO 4",
        "ALTICE BUSINESS FIT CONTROLADO": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "ALTICE BUSINESS FIT CONTROLADO - ALTICE BUSINESS FIT CONTROLADO 150": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "ALTICE CARD": "4 - CARD",
        "ALTICE CARD CANARIO": "4 - CARD",
        "ALTICE PREPAGO": "4 - CARD",
        "ALTICE PREPAGO - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "ALTICE PREPAGO - CARD": "4 - CARD",
        "ALTICE PREPAGO REGIONAL": "4 - CARD",
        "ALTICE PREPAGO SIMO": "322 - GRUPO CARD SIM ONLY",
        "ALTICE PREPAGO SIMO - APPS LARGE 200 MIN / 4GB": "886 - GRUPO 3",
        "ALTICE PREPAGO SIMO - APPS LARGE 200 MIN / 7GB + 23GB": "887 - GRUPO 4",
        "ALTICE PREPAGO SIMO - APPS MEDIUM 100 MIN / 3GB + 12GB": "885 - GRUPO 2",
        "ALTICE PREPAGO SIMO - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
        "ALTICE PREPAGO SIMO - APPS MEDIUM 200MIN / 5GB + 20GB": "886 - GRUPO 3",
        "ALTICE PREPAGO SIMO - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "ALTICE PREPAGO SIMO - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "ALTICE PREPAGO SIMO - APPS SMALL 100 MIN / 2GB + 5GB": "884 - GRUPO 1",
        "ALTICE PREPAGO SIMO - CARD": "322 - GRUPO CARD SIM ONLY",
        "ALTICE PREPAGO SIMO - PRO SMALL 200 MIN / 8GB +27GB": "888 - GRUPO 5",
        "ALTICE PREPAGO SIMO - PRO SMALL 300 MIN / 10GB + 35GB": "888 - GRUPO 5",
        "ALTICE PREPAGO SIMO - SIMO DATA": "323 - GRUPO CARD SIMO DATA",
        "ALTICE PREPAGO SIMO (DEALER)": "322 - GRUPO CARD SIM ONLY",
        "ALTICE PREPAGO SIMO REGIONAL": "323 - GRUPO CARD SIMO DATA",
        "ALTICE PREPAGO SIMO REGIONAL - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "BUSINESS FIT": "831 - ACTIV-NEGOCIOS-GRUPO 6",
        "BUSINESS FIT CERRADO": "829 - ACTIV-NEGOCIOS-GRUPO 4",
        "BUSINESS FIT CONTROLADO": "831 - ACTIV-NEGOCIOS-GRUPO 6",
        "FLEX": "889 - GRUPO 6",
        "FLEX - APPS LARGE 200 MIN / 4GB": "886 - GRUPO 3",
        "FLEX - APPS LARGE 200 MIN / 7GB + 23GB": "887 - GRUPO 4",
        "FLEX - APPS MEDIUM 100 MIN / 3GB + 12GB": "885 - GRUPO 2",
        "FLEX - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
        "FLEX - APPS MEDIUM 200MIN / 5GB + 20GB": "886 - GRUPO 3",
        "FLEX - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "FLEX - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "FLEX - APPS SMALL 100 MIN / 2GB + 5GB": "884 - GRUPO 1",
        "FLEX - APPS XLARGE 200 MIN / 5GB": "887 - GRUPO 4",
        "FLEX - CARD": "322 - GRUPO CARD SIM ONLY",
        "FLEX - PRO EXTRA LARGE 1000 MIN / 35GB": "912 - GRUPO 12",
        "FLEX - PRO EXTRA LARGE 300 MIN / 25GB +75GB": "893 - GRUPO 9",
        "FLEX - PRO EXTRA LARGE 300 MIN / 35GB": "895 - GRUPO 11",
        "FLEX - PRO EXTRA LARGE 500 MIN / 25GB +90GB": "894 - GRUPO 10",
        "FLEX - PRO EXTRA LARGE 500 MIN / 35GB": "895 - GRUPO 11",
        "FLEX - PRO LARGE 200 MIN / 20GB +45GB": "890 - GRUPO 7",
        "FLEX - PRO LARGE 200 MIN / 25GB": "893 - GRUPO 9",
        "FLEX - PRO LARGE 300 MIN / 20GB + 50GB": "891 - GRUPO 8",
        "FLEX - PRO LARGE 300 MIN / 25GB": "893 - GRUPO 9",
        "FLEX - PRO LARGE 500 MIN / 25GB": "894 - GRUPO 10",
        "FLEX - PRO MEDIUM 150 MIN / 20GB": "890 - GRUPO 7",
        "FLEX - PRO MEDIUM 200 MIN / 15GB + 35GB": "889 - GRUPO 6",
        "FLEX - PRO MEDIUM 200 MIN / 20GB": "890 - GRUPO 7",
        "FLEX - PRO MEDIUM 300 MIN / 15GB + 40GB": "889 - GRUPO 6",
        "FLEX - PRO MEDIUM 300 MIN / 20GB": "891 - GRUPO 8",
        "FLEX - PRO MEDIUM 500 MIN / 20GB": "893 - GRUPO 9",
        "FLEX - PRO SMALL 100 MIN / 10GB": "889 - GRUPO 6",
        "FLEX - PRO SMALL 200 MIN / 10GB": "889 - GRUPO 6",
        "FLEX - PRO SMALL 200 MIN / 8GB +27GB": "888 - GRUPO 5",
        "FLEX - PRO SMALL 300 MIN / 10GB": "889 - GRUPO 6",
        "FLEX - PRO SMALL 300 MIN / 10GB + 35GB": "888 - GRUPO 5",
        "FLEX - PRO SMALL 500 MIN / 10GB": "891 - GRUPO 8",
        "FLEX - PRO ULTRA 1000MIN / 30GB + 130GB": "912 - GRUPO 12",
        "FLEX - PRO ULTRA 300MIN / 30GB + 130GB": "895 - GRUPO 11",
        "FLEX - PRO ULTRA 500MIN / 30GB + 130GB": "895 - GRUPO 11",
        "FLEX - PRO XSMALL 100 MIN / 7GB": "888 - GRUPO 5",
        "FLEX ALTICE - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "FLEX ARDILLA": "884 - GRUPO 1",
        "FLEX ARDILLA - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
        "FLEX ARDILLA - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "FLEX ARDILLA - APPS SMALL 100 MIN / 2GB + 5GB": "884 - GRUPO 1",
        "FLEX ARDILLA LOS MIOS": "884 - GRUPO 1",
        "FLEX ARDILLA LOS MIOS - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "FLEX CANARIO": "888 - GRUPO 5",
        "FLEX CANARIO - APPS MEDIUM 200MIN / 5GB + 20GB": "886 - GRUPO 3",
        "FLEX CANARIO N/FDS": "885 - GRUPO 2",
        "FLOTILLA": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA ADICIONAL": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA ALTICE BUSINESS": "285 - ACTIV-NEGOCIOS-GRUPO 2",
        "FLOTILLA ALTICE BUSINESS ADICIONAL": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA ALTICE BUSINESS FLEX": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA ALTICE BUSINESS FLEX ADICIONAL": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA FM": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA FM ADICIONAL": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA FM GRUPO": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA FM GRUPO ADICIONAL": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA NET ADICIONAL": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA NET ALTICE BUSINESS": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA NET ALTICE BUSINESS ADICIONAL": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA NET FM": "284 - ACTIV-NEGOCIOS-GRUPO 1",
        "FLOTILLA NET FM ADICIONAL": "285 - ACTIV-NEGOCIOS-GRUPO 2",
        "FLOTILLA NET FM GRUPO": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "FLOTILLA NET FM GRUPO ADICIONAL": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "INDIVIDUAL": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "INDIVIDUAL CERRADO": "286 - ACTIV-NEGOCIOS-GRUPO 3",
        "INDIVIDUAL CONTROLADO": "829 - ACTIV-NEGOCIOS-GRUPO 4",
        "INTERNET ALTICE-F": "802 - GRUPO NET 6 - 18 MESES",
        "INTERNET ALTICE-F - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET ALTICE-F - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET ALTICE-F - 20GB BEST EFFORT": "802 - GRUPO NET 6 - 18 MESES",
        "INTERNET ALTICE-F - 25GB BEST EFFORT": "803 - GRUPO NET 7 - 18 MESES",
        "INTERNET ALTICE-F - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-F - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "INTERNET ALTICE-F - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "INTERNET ALTICE-F REGIONAL - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "INTERNET ALTICE-M": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET ALTICE-M - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET ALTICE-M - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET ALTICE-M - 20GB BEST EFFORT": "802 - GRUPO NET 6 - 18 MESES",
        "INTERNET ALTICE-M - 25GB BEST EFFORT": "803 - GRUPO NET 7 - 18 MESES",
        "INTERNET ALTICE-M - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-M - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "INTERNET ALTICE-M - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "INTERNET ALTICE-M REGIONAL": "465 - GRUPO NET 2 - 18 MESES",
        "INTERNET ALTICE-M REGIONAL - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET ALTICE-M REGIONAL - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-M REGIONAL - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "INTERNET ALTICE-M REGIONAL - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "INTERNET MBB - INTERNET MBB 1 + 2GB": "972 - GRUPO MBB 0 - 36 MESES",
        "INTERNET MOVIL ALTICE": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET MOVIL ALTICE - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET MOVIL ALTICE - 20GB BEST EFFORT": "802 - GRUPO NET 6 - 18 MESES",
        "INTERNET MOVIL ESTUDIANTES": "804 - GRUPO NET 0 - 12 MESES (EST)",        
        "INTERNET MOVIL PREPAGO - ALTICE TRAVEL PACK": "482 - GRUPO NET 0 - 12 MESES",
        "INTERNET MOVIL PREPAGO - PAQUETE 2GB X 15 DIAS A $599": "482 - GRUPO NET 0 - 12 MESES",
        "INTERNET MOVIL PREPAGO - Paquete Internet móvil prepago": "482 - GRUPO NET 0 - 12 MESES",
        "INTERNET NEGOCIOS ALTICE-F": "477 - GRUPO NET 4 - 18 MESES (NEG)",
        "INTERNET NEGOCIOS ALTICE-M": "477 - GRUPO NET 4 - 18 MESES (NEG)",
        "M2M CONTROL": "242 - Altice NET DATA PRE PAGO",        
        "MAX - APPS LARGE 200 MIN / 4GB": "886 - GRUPO 3",
        "MAX - APPS LARGE 200 MIN / 7GB + 23GB": "887 - GRUPO 4",
        "MAX - APPS MEDIUM 100 MIN / 3GB + 12GB": "885 - GRUPO 2",
        "MAX - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
        "MAX - APPS MEDIUM 200MIN / 5GB + 20GB": "886 - GRUPO 3",
        "MAX - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "MAX - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "MAX - APPS SMALL 100 MIN / 2GB + 5GB": "884 - GRUPO 1",
        "MAX - APPS XLARGE 200 MIN / 5GB": "887 - GRUPO 4",
        "MAX - PRO EXTRA LARGE 1000 MIN / 35GB": "912 - GRUPO 12",
        "MAX - PRO EXTRA LARGE 300 MIN / 25GB +75GB": "893 - GRUPO 9",
        "MAX - PRO EXTRA LARGE 300 MIN / 35GB": "895 - GRUPO 11",
        "MAX - PRO EXTRA LARGE 500 MIN / 25GB +90GB": "894 - GRUPO 10",
        "MAX - PRO EXTRA LARGE 500 MIN / 35GB": "895 - GRUPO 11",
        "MAX - PRO LARGE 200 MIN / 20GB +45GB": "890 - GRUPO 7",
        "MAX - PRO LARGE 200 MIN / 25GB": "893 - GRUPO 9",
        "MAX - PRO LARGE 300 MIN / 20GB + 50GB": "891 - GRUPO 8",
        "MAX - PRO LARGE 300 MIN / 25GB": "893 - GRUPO 9",
        "MAX - PRO LARGE 500 MIN / 25GB": "894 - GRUPO 10",
        "MAX - PRO MEDIUM 150 MIN / 20GB": "890 - GRUPO 7",
        "MAX - PRO MEDIUM 200 MIN / 15GB + 35GB": "889 - GRUPO 6",
        "MAX - PRO MEDIUM 200 MIN / 20GB": "890 - GRUPO 7",
        "MAX - PRO MEDIUM 300 MIN / 15GB + 40GB": "889 - GRUPO 6",
        "MAX - PRO MEDIUM 300 MIN / 20GB": "891 - GRUPO 8",
        "MAX - PRO MEDIUM 500 MIN / 20GB": "893 - GRUPO 9",
        "MAX - PRO SMALL 100 MIN / 10GB": "889 - GRUPO 6",
        "MAX - PRO SMALL 200 MIN / 10GB": "889 - GRUPO 6",
        "MAX - PRO SMALL 200 MIN / 8GB +27GB": "888 - GRUPO 5",
        "MAX - PRO SMALL 300 MIN / 10GB": "889 - GRUPO 6",
        "MAX - PRO SMALL 300 MIN / 10GB + 35GB": "888 - GRUPO 5",
        "MAX - PRO SMALL 500 MIN / 10GB": "891 - GRUPO 8",
        "MAX - PRO ULTRA 1000MIN / 30GB + 130GB": "912 - GRUPO 12",
        "MAX - PRO ULTRA 300MIN / 30GB + 130GB": "895 - GRUPO 11",
        "MAX - PRO ULTRA 500MIN / 30GB + 130GB": "895 - GRUPO 11",
        "MAX - PRO XSMALL 100 MIN / 7GB": "888 - GRUPO 5",
        "MAX CANARIO": "885 - GRUPO 2",
        "MAX CANARIO - PRO XSMALL 100 MIN / 7GB": "888 - GRUPO 5",
        "MAX LEOPARDO": "893 - GRUPO 9",
        "NUEVO BUSINESS FIT": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "NUEVO BUSINESS FIT CERRADO": "829 - ACTIV-NEGOCIOS-GRUPO 4",
        "NUEVO BUSINESS FIT CONTROLADO": "833 - ACTIV-NEGOCIOS-GRUPO 8",
        "NUEVO INTERNET ALTICE-M": "802 - GRUPO NET 6 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 20GB BEST EFFORT": "802 - GRUPO NET 6 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 25GB BEST EFFORT": "803 - GRUPO NET 7 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "PLAN 200MIN/10GB + BONO 5GB - INDOTEL": "830 - ACTIV-NEGOCIOS-GRUPO 5",
        "RT - FLEX BASICO": "883 - GRUPO 0",
        "RT - FLEX BASICO - APPS LARGE 200 MIN / 4GB": "886 - GRUPO 3",
        "RT - FLEX BASICO - APPS LARGE 200 MIN / 7GB + 23GB": "887 - GRUPO 4",
        "RT - FLEX BASICO - APPS MEDIUM 100 MIN / 3GB + 12GB": "885 - GRUPO 2",
        "RT - FLEX BASICO - APPS MEDIUM 150 MIN / 2GB": "885 - GRUPO 2",
        "RT - FLEX BASICO - APPS MEDIUM 200MIN / 5GB + 20GB": "886 - GRUPO 3",
        "RT - FLEX BASICO - APPS SMALL 100 MIN / 1GB": "884 - GRUPO 1",
        "RT - FLEX BASICO - APPS SMALL 100 MIN / 1GB + 2GB": "884 - GRUPO 1",
        "RT - FLEX BASICO - APPS SMALL 100 MIN / 2GB + 5GB": "884 - GRUPO 1",
        "RT - FLEX BASICO - PRO MEDIUM 200 MIN / 15GB + 35GB": "889 - GRUPO 6",
        "RT - FLEX BASICO - PRO SMALL 200 MIN / 8GB +27GB": "888 - GRUPO 5",
        "RT - FLEX BASICO - PRO XSMALL 100 MIN / 7GB": "888 - GRUPO 5",
        "RT - INTERNET ALTICE- F": "464 - GRUPO NET 1 - 18 MESES",
        "RT - INTERNET ALTICE- F - 10GB BEST EFFORT ESPECIAL": "467 - GRUPO NET 4 - 18 MESES",
        "RT - INTERNET ALTICE- F - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "RT - INTERNET ALTICE- M": "464 - GRUPO NET 1 - 18 MESES",
        "RT - INTERNET ALTICE- M - 15GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "RT - INTERNET ALTICE- M - 3GB REGIONAL BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "RT - INTERNET ALTICE- M - 5GB REGIONAL BEST EFFORT": "465 - GRUPO NET 2 - 18 MESES",
        "RT - INTERNET ALTICE- M - 7GB BEST EFFORT": "466 - GRUPO NET 3 - 18 MESES",
        "STAFF ALTICE": "6 - STAFF",
        "INTERNET MOVIL ALTICE - 1MBPS/1MBPS MOVIL": "464 - GRUPO NET 1 - 18 MESES",
        "RT - INTERNET ALTICE- F - 2GB BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "RT - INTERNET ALTICE- M - 2GB BEST EFFORT": "464 - GRUPO NET 1 - 18 MESES",
        "INTERNET ALTICE-F - 10GB BEST EFFORT": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET MOVIL ESTUDIANTES - VELOCIDAD 10MBPS/256KBPS": "467 - GRUPO NET 4 - 18 MESES",
        "INTERNET MOVIL ALTICE - 3MBPS/1.5MBPS MOVIL": "471 - GRUPO NET 5 - 18 MESES",
        "INTERNET ALTICE-M - 10GB BEST EFFORT": "471 - GRUPO NET 5 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 6GB": "465 - GRUPO NET 2 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 8GB": "466 - GRUPO NET 3 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 12GB": "467 - GRUPO NET 4 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 18GB": "471 - GRUPO NET 5 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 22GB": "802 - GRUPO NET 6 - 18 MESES",
        "NUEVO INTERNET ALTICE-M - NEW INTERNET ALTICE 30GB": "803 - GRUPO NET 7 - 18 MESES",
        "FLEX - BASICO 70MIN / 70MB": "883 - GRUPO 0",
        "FLEX - BASICO 60MIN / 30MB": "883 - GRUPO 0",
        "FLEX ARDILLA - ARDILLA 60 MIN + 60 SMS (FLEX)": "883 - GRUPO 0",
        "FLEX ARDILLA LOS MIOS - ARDILLA 30 MIN + 30 MIN (FLEX)": "883 - GRUPO 0",
        "RT - FLEX BASICO - BASICO 50MIN /1GB": "883 - GRUPO 0",
        "RT - FLEX BASICO - BASICO 50MIN": "883 - GRUPO 0",
        "RT - FLEX BASICO - BASICO 60MIN / 30MB": "883 - GRUPO 0",
        "RT - FLEX BASICO - BASICO 60MIN / 2GB": "883 - GRUPO 0",
        "FLEX - APPS 100 MINUTOS/1GB": "884 - GRUPO 1",
        "FLEX - APPS 75 MINUTOS/700MB": "884 - GRUPO 1",
        "FLEX - APPS XSMALL 100 MIN / 100MB": "884 - GRUPO 1",
        "FLEX - PLAN APPS 100MIN/100MB": "884 - GRUPO 1",
        "FLEX - APPS SMALL 150 MIN / 250MB": "885 - GRUPO 2",
        "FLEX - BASICO150MIN / 100MB": "885 - GRUPO 2",
        "FLEX - PLAN APPS 200MIN/100MB": "885 - GRUPO 2",
        "FLEX - APPS ESPECIAL DE 200 MIN / 4GB": "886 - GRUPO 3",
        "FLEX - APPS MEDIUM 200 MIN / 700MB": "886 - GRUPO 3",
        "FLEX - BASICO250MIN / 500MB": "886 - GRUPO 3",
        "FLEX - PLAN APPS PLUS 100MIN/500MB": "886 - GRUPO 3",
        "FLEX - PLAN APPS PLUS 200MIN/500MB": "886 - GRUPO 3",
        "MAX - APPS MEDIUM 200 MIN / 700MB": "886 - GRUPO 3",
        "FLEX - APPS MEDIUM 200 MIN / 5GB + 20GB": "886 - GRUPO 3",
        "FLEX - APPS LARGE 200 MIN / 1GB": "887 - GRUPO 4",
        "FLEX - BASICO 300MIN / 1GB": "887 - GRUPO 4",
        "FLEX - PLAN APPS FULL 100MIN/1GB": "887 - GRUPO 4",
        "FLEX - APPS LARGE 250 MIN / 2GB": "888 - GRUPO 5",
        "FLEX - PLAN APPS FULL 200MIN/1GB": "888 - GRUPO 5",
        "FLEX - PRO ESPECIAL DE 100 MIN / 7GB": "888 - GRUPO 5",
        "FLEX - PRO XSMALL 100 MIN / 2GB": "888 - GRUPO 5",
        "MAX - PRO XSMALL 100 MIN / 2GB": "888 - GRUPO 5",
        "FLEX - PRO SMALL 100 MIN / 4GB": "889 - GRUPO 6",
        "FLEX - PRO SMALL 200 MIN / 4GB": "889 - GRUPO 6",
        "MAX - PRO SMALL 200 MIN / 4GB": "889 - GRUPO 6",
        "MAX - PLAN PRO 100MIN/5GB": "889 - GRUPO 6",
        "MAX - PRO SMALL 300 MIN / 4GB": "889 - GRUPO 6",
        "FLEX - PRO MEDIUM 150 MIN / 7GB": "890 - GRUPO 7",
        "FLEX - PRO MEDIUM 200 MIN / 7GB": "890 - GRUPO 7",
        "MAX - PRO MEDIUM 200 MIN / 7GB": "890 - GRUPO 7",
        "FLEX - PRO MEDIUM 300 MIN / 7GB": "891 - GRUPO 8",
        "FLEX - PRO SMALL 500 MIN / 4GB": "891 - GRUPO 8",
        "MAX - PRO MEDIUM 300 MIN / 7GB": "891 - GRUPO 8",
        "FLEX - PRO LARGE 200 MIN / 14GB": "893 - GRUPO 9",
        "MAX - PRO MEDIUM 500 MIN / 7GB": "893 - GRUPO 9",
        "FLEX - PRO LARGE 300 MIN / 14GB": "893 - GRUPO 9",
        "MAX - PRO LARGE 300 MIN / 14GB": "893 - GRUPO 9",
        "MAX - PRO LARGE 200 MIN / 14GB + 50GB": "893 - GRUPO 9",
        "MAX - PRO LARGE 200 MIN / 14GB": "893 - GRUPO 9",
        "FLEX - PRO LARGE 500 MIN / 14GB": "894 - GRUPO 10",
        "MAX - PRO LARGE 500 MIN / 14GB": "894 - GRUPO 10",
        "MAX - PRO EXTRA LARGE 1000 MIN / 25GB": "912 - GRUPO 12",        
        "FLEX - APPS SMALL 100 MIN / 1GB + 2GB BONO":"884 - GRUPO 1",
        "RT - FLEX BASICO - APPS SMALL 100 MIN / 1GB + 2GB BONO":"884 - GRUPO 1",
        "FLEX - APPS SMALL 100 MIN / 2GB + 5GB BONO":"884 - GRUPO 1",
        "FLEX - APPS MEDIUM 100 MIN / 3GB + 12GB BONO":"885 - GRUPO 2",
        "FLEX - APPS MEDIUM 200MIN / 5GB + 20GB BONO":"886 - GRUPO 3",
        "RT - FLEX BASICO - APPS MEDIUM 200MIN / 5GB + 20GB BONO":"	886 - GRUPO 3",
        "FLEX - APPS LARGE 200 MIN / 7GB + 23GB BONO":"887 - GRUPO 4",
        "FLEX - PRO SMALL 200 MIN / 8GB +27GB BONO":"888 - GRUPO 5",
        "FLEX - PRO SMALL 300 MIN / 10GB + 35GB BONO":"888 - GRUPO 5",
        "MAX - PRO SMALL 300 MIN / 10GB + 35GB BONO":"888 - GRUPO 5",
        "FLEX - PRO MEDIUM 200 MIN / 15GB + 35GB BONO":"889 - GRUPO 6",
        "FLEX - PRO MEDIUM 300 MIN / 15GB + 40GB BONO":"889 - GRUPO 6",
        "FLEX - PRO LARGE 200 MIN / 20GB +45GB BONO":"890 - GRUPO 7",
        "FLEX - PRO LARGE 300 MIN / 20GB + 50GB BONO":"891 - GRUPO 8",
        "MAX - PRO EXTRA LARGE 300 MIN / 25GB +75GB BONO":"893 - GRUPO 9",
        "FLEX - PRO EXTRA LARGE 500 MIN / 25GB +90GB BONO":"894 - GRUPO 10",
        "FLEX - APPS MEDIUM 200MIN / 5GB + 20GB BONO":"886 - GRUPO 3",
        "FLEX - APPS MEDIUM 100 MIN / 3GB + 12GB BONO":"885 - GRUPO 2",
        "FLEX - PRO EXTRA LARGE 300 MIN / 25GB +75GB BONO":"893 - GRUPO 9",   
        "MAX - APPS SMALL 100 MIN / 2GB + 5GB BONO":"884 - GRUPO 1",
        "MAX - PRO SMALL 200 MIN / 8GB +27GB BONO":"888 - GRUPO 5",
        "MAX - PRO LARGE 300 MIN / 20GB + 50GB BONO":"891 - GRUPO 8",
        }

        mapeo_negocios_grupos = {
            "284 - ACTIV-NEGOCIOS-GRUPO 1":"884 - GRUPO 1",
            "285 - ACTIV-NEGOCIOS-GRUPO 2":"885 - GRUPO 2",
            "286 - ACTIV-NEGOCIOS-GRUPO 3":"886 - GRUPO 3",
            "829 - ACTIV-NEGOCIOS-GRUPO 4":"887 - GRUPO 4",
            "830 - ACTIV-NEGOCIOS-GRUPO 5":"888 - GRUPO 5",
            "831 - ACTIV-NEGOCIOS-GRUPO 6":"889 - GRUPO 6",
            "290 - ACTIV-NEGOCIOS-GRUPO 7":"890 - GRUPO 7",
            "833 - ACTIV-NEGOCIOS-GRUPO 8":"891 - GRUPO 8",
            "292 - ACTIV-NEGOCIOS-GRUPO 9":"893 - GRUPO 9",
            "293 - ACTIV-NEGOCIOS-GRUPO 10":"894 - GRUPO 10",
            "294 - ACTIV-NEGOCIOS-GRUPO 11":"895 - GRUPO 11",
            "295 - ACTIV-NEGOCIOS-GRUPO 12":"912 - GRUPO 12",
            "477 - GRUPO NET 4 - 18 MESES (NEG)":"467 - GRUPO NET 4 - 18 MESES",
            "474 - GRUPO NET 5 NEGOCIOS - 18 MESES":"471 - GRUPO NET 5 - 18 MESES",

        }

        mapeo_condiciones_ventacosto = {
            "1325 - VENTA DE EQUIPOS AL COSTO": "0"            
        }   
    
        mapeo_condiciones_Up_Down = {
            "5000 - AUMENTO DE PLAN CON VENTA EQUIPO POR REEMPLAZO":"0",
            "5001 - AUMENTO DE PLAN CON VENTA EQUIPO POR FIDE":"0",
            "5030 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR REEMPLAZO":"0",
            "5031 - DISMINUCIÓN DE PLAN CON VENTA EQUIPO POR FIDE":"0",
        }

        try:           
            #Limpiar espacios en los nombres de las columnas de planes
            if 'nom_plan' in df.columns:
                 df['nom_plan'] = df['nom_plan'].astype('string').str.strip() 
            if 'nom_plan_anterior' in df.columns:
                df['nom_plan_anterior'] = df['nom_plan_anterior'].astype('string').str.strip() 

            # Normalizar columnas numéricas, truncando decimales para asegurar conversión a entero.
            text_cols = ['telefono', 'imei', 'id_transaccion', 'sim', 'tel_contacto', 'tel_contacto2']
            for col in text_cols:
                if col in df.columns:
                    # Convertir a string y quitar '.0'
                    df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True) 
                    # Reemplazar "nan" o "None" (que se volvieron strings) por un nulo real de Pandas
                    df[col] = df[col].replace(['nan', 'None', '<NA>', ''], pd.NA)

            # Función para modificar la columna según la condición, y aplicar el grupo correcto.
            def modificar_valor(row: pd.Series) -> str | None:
                return mapeo_condiciones_grupos.get(
                    row["nom_plan_anterior"], row["grupo_activacion_anterior"]
                )

            def modificar_ventacosto(row):
                return mapeo_condiciones_ventacosto.get(
                    row["razon_servicio"], row["grupo_activacion_orden"]
                )

            def modificar_grupo(row):
                return mapeo_negocios_grupos.get(
                    row["grupo_activacion_orden"], row["grupo_activacion_orden"]
                )

            def modificar_UpDown(row):
                return mapeo_condiciones_Up_Down.get(
                    row["razon_servicio"], row["grupo_activacion_anterior"]
                )

            # Aplicar la función a las columnas que se desean modificar
            df["grupo_activacion_anterior"] = df.apply(modificar_valor, axis=1) # type: ignore
            df["grupo_activacion_anterior"] = df.apply(modificar_UpDown, axis=1) # type: ignore
            df["grupo_activacion_orden"] = df.apply(modificar_ventacosto, axis=1) # type: ignore
            df["grupo_activacion_orden"] = df.apply(modificar_grupo, axis=1) # type: ignore

            # Lista de condiciones para eliminar filas y limpiar datos innecesarios.
            condiciones_usuario = ["OS - SISTEMA ORDENES(AUTOMATICO)"] 
            condiciones_razon_servicio = [
                "1159 - MISCELANEOS VIDEO ON DEMAND",
                "1309 - ACTIVACIONES Y DESACTIVACIÓN SERVICIOS OPCIONALES",
                "1304 - USO DE FIDEPUNTOS (HABLA MAS / P&S)",
                "1312 - TRANSFERENCIA FIDEPUNTOS",
                "1315 - CAMBIO DE NUMERO",
                "1365 - CAMBIO DE NUMERO (PORTABILIDAD)",
                "1369 - RECONEXION POR ROBO / PÉRDIDA",
                "1372 - SEPARACION DE CUENTAS",
                "1400 - TRASPASO DE CONTRATO  PREPAGO",
                "1376 - UNIFICACION DE CUENTAS",
                "1318 - DISMINUCION PRODUCTO POSTPAGO-PREPAGO",
                "1352 - SUSPENSION TEMPORAL (90 DIAS)",
                "1331 - POR ERROR DE DIGITACIÓN",
                "1368 - RECONEXIÓN DE SERVICIO",
                "1327 - A SOLICITUD DEL CLIENTE",
                "1351 - SUSPENSION TEMPORAL (60 DIAS)",
                "1329 - SUSPENSIÓN DE SERVICIO POR PÉRDIDA O ROBO",
                "349 - RETIRO QUITESE",
                "5020 - TITULAR CON VALIDADOR DE IDENTIDAD",
                "1323 - DISMINUCIÓN DE PLAN / PAQUETE",
                "1319 - DISMINUCIÓN DE PRODUCTO POSTPAGO-POSTPAGO",
                "1226 - CAMBIO DE PLAN MIGRACION DE ALTICE DOMINICANA",
                "1328 - SUSPENSION TEMPORAL (30 DIAS)",
                "1509 - ACTIV Y DESACTIV SERVICIO OPCIONAL VIRTUAL",
                "29 - RECONEXION DEUDA SALDADA",
                "350 - RETIRO QUITESE MOBCEL",
                "43 - MISCELANEOS LOGICOS",
                "484 - CORRECCIÓN CONTRATO",
                "6513 - CAMBIO NUMERO PORTABILIDAD ALTICE - ALTICE",
            ]            

            # Crear una condición compuesta para eliminar filas y datos innecesarios
            condicion = (
                (df["usuario_creo_orden"].isin(condiciones_usuario))
                | (df["razon_servicio"].isin(condiciones_razon_servicio))                
            )

            # Eliminar las filas que cumplen la condición
            df.drop(df[condicion].index, inplace=True)

            if not df.empty:
                columnas_valida = [
                    "id_transaccion",
                    "fecha_digitacion_orden",
                    "fecha_termino_orden",
                    "estado_transaccion",
                    "usuario_creo_orden",
                    "entity_code",
                    "subcanal",
                    "tipo_actividad",
                    "razon_servicio",
                    "telefono",
                    "imei",
                    "nom_plan",
                    "nom_plan_anterior",
                    "grupo_activacion_orden",
                    "grupo_activacion_anterior",
                ]

                # Filtrar las columnas de interés
                filtrado = df[columnas_valida].copy()

                # 1. Convertir Fechas (DATE)
                # errors='coerce' convierte fechas inválidas en NaT (Not a Time), que se vuelve NULL
                filtrado.loc[:, 'fecha_digitacion_orden'] = pd.to_datetime(filtrado['fecha_digitacion_orden'], errors='coerce')
                filtrado.loc[:, 'fecha_termino_orden'] = pd.to_datetime(filtrado['fecha_termino_orden'], errors='coerce')
                
                # 2. Convertir Enteros (INTEGER)
                # Usamos Int64 (con 'I' mayúscula) porque soporta nulos (pd.NA)
                if 'subcanal' in filtrado.columns:
                    filtrado.loc[:, 'subcanal'] = pd.to_numeric(filtrado['subcanal'], errors='coerce').astype('Int64')

                #imei_nulo = filtrado['imei'].isnull()

                # Para esas filas, reemplazar 'imei' con el valor de 'telefono'
                #filtrado.loc[imei_nulo, 'imei'] = filtrado.loc[imei_nulo, 'telefono']
                filtrado['imei'] = filtrado['imei'].fillna("111111111111111")
                filtrado['telefono'] = filtrado['telefono'].fillna("8095999999")               
                
                # Eliminar duplicados
                filtrado = filtrado.drop_duplicates(
                    subset=["fecha_digitacion_orden", "id_transaccion", "razon_servicio", "telefono"],
                    keep="last",
                )                
                
                # Guardar en tabla transacciones
                if not filtrado.empty:
                    cn.guardar_filtrado_en_db(filtrado)
                    # Mostrar mensaje de confirmación
                    print("Procesamiento completado y datos guardados en la base de datos. 1")
                    return jsonify({"status": "success", "message": "Datos procesados y guardados correctamente."})
                else:
                    print("No se encontraron datos válidos para procesar.")
                    return jsonify({"status": "error", "message": "No se encontraron datos válidos para procesar."}), 400

            else:
                print("No se encontraron datos válidos para procesar después del filtrado.")
                return jsonify({"status": "error", "message": "No se encontraron datos válidos para procesar después del filtrado."}), 400

        except Exception as e:
            print(f"Error al procesar el dataframe: {e}")
            return jsonify({"status": "error", "message": f"Error al procesar el dataframe: {e}"}), 500
            
    except Exception as e:
        print(f"Error al procesar los datos: {e}")
        return jsonify({"status": "error", "message": f"Error al procesar los datos: {e}"}), 500

# ------------------------------------------------------
# Función auxiliar para normalizar valores tipo texto
# ------------------------------------------------------
def limpiar_campo_texto(serie):
    """Convierte valores numéricos a texto, elimina '.0', espacios, y normaliza."""
    # Convertir a string y limpiar
    serie_str = (
        serie.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .str.replace(r"\s+", "", regex=True)
        .str.upper()  # opcional: unifica mayúsculas/minúsculas
    )
    # Reemplazar los strings 'NAN', 'NONE', 'NULL' etc., por un nulo verdadero de Pandas (pd.NA)
    serie_str = serie_str.replace(['NAN', 'NONE', '<NA>', 'NULL', ''], pd.NA)
    return serie_str