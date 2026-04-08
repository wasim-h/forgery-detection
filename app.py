import streamlit as st
from PIL import Image
import io
from dotenv import load_dotenv
from analyzer import analyze_document

load_dotenv()

st.set_page_config(
    page_title="ID Forgery Detector",
    layout="centered"
)

st.title("🔍 ID Forgery Detector")
st.caption("Upload an ID document image to check for signs of tampering or forgery.")

upload_file = st.file_uploader(
    "Upload ID Document",
    type=["jpg", "jpeg", "png", "webp"],
    help="Supported formats: jpg, jpeg, png, webp — Max 5MB"
)

if upload_file:
    if upload_file.size > 5 * 1024 * 1024:
        st.error("File too large. Please upload an image under 5MB.")
        st.stop()

    image = Image.open(upload_file)
    st.image(image, caption="Uploaded Document", width=600)

    if st.button("Analyze Document", type="primary"):
        with st.spinner("Analyzing document for forgery indicators..."):
            try:
                img_byte = io.BytesIO()
                fmt = image.format or "JPEG"
                image.save(img_byte, format=fmt)
                img_byte.seek(0)
                img_byte = img_byte.getvalue()

                media_type_map = {
                    "JPEG": "image/jpeg",
                    "PNG": "image/png",
                    "WEBP": "image/webp"
                }
                media_type = media_type_map.get(fmt, "image/jpeg")
                result = analyze_document(img_byte, media_type)

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.stop()

        verdict = result.get("verdict", "UNKNOWN")
        risk = result.get("risk_score", 0)
        summary = result.get("summary", "")

        if verdict == "GENUINE":
            st.success(f"GENUINE — Risk Score: {risk}/100")
        elif verdict == "SUSPICIOUS":
            st.warning(f"SUSPICIOUS — Risk Score: {risk}/100")
        else:
            st.error(f"LIKELY FORGED — Risk Score: {risk}/100")

        st.markdown(f"**Summary:** {summary}")
        st.divider()

        st.subheader("Detailed Findings")
        findings = result.get("findings", [])

        for f in findings:
            status = f.get("status", "OK")
            category = f.get("category", "")
            detail = f.get("detail", "")

            if status == "OK":
                st.success(f"**{category}** — {detail}")
            elif status == "WARNING":
                st.warning(f"**{category}** — {detail}")
            else:
                st.error(f"**{category}** — {detail}")

        st.divider()

        red_flags = result.get("red_flags", [])
        if red_flags:
            st.subheader("Red Flags")
            for flag in red_flags:
                st.markdown(f"-{flag}")
            st.divider()

        st.subheader("Recommendation")
        st.info(result.get("recommendation", ""))