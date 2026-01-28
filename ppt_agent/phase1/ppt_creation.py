import streamlit as st
import os
import comtypes.client
import tempfile
import pythoncom
import base64

def show_pdf(file_path):
    """Display PDF in Streamlit using base64 encoding and iframe"""
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.title("PPT Viewer")

pptx_path = r"Documents\cursor\agents_learning\ppt_agent\rajasthan_water_scarcity_csr.pptx"

if os.path.exists(pptx_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "slides.pdf")
        try:
            pythoncom.CoInitialize()
            powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
            powerpoint.Visible = 1
            
            abs_pptx = os.path.abspath(pptx_path)
            abs_pdf = os.path.abspath(pdf_path)
            
            presentation = powerpoint.Presentations.Open(abs_pptx, ReadOnly=True, WithWindow=False)
            presentation.SaveAs(abs_pdf, 32)
            presentation.Close()
            powerpoint.Quit()
            pythoncom.CoUninitialize()
            
            if os.path.exists(abs_pdf):
                show_pdf(abs_pdf)
            else:
                st.error("Conversion failed")
                
        except Exception as e:
            st.error(f"Error: {e}")
            try:
                pythoncom.CoUninitialize()
            except:
                pass
else:
    st.error("File not found")
