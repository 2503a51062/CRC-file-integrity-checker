import streamlit as st
import OS

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="CRC-32 File Integrity Checker",
    page_icon="🔐",
    layout="wide"
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🔐 CRC-32 Based File Integrity Checker")

st.write(
    "Upload the original file and the current file to verify "
    "whether the file contents have changed."
)

st.info(
    "CRC-32 compares the contents of two files. "
    "If their CRC-32 values are the same, the contents match."
)

# --------------------------------------------------
# CRC-32 FUNCTION
# --------------------------------------------------

def calculate_crc32(uploaded_file):
    """
    Calculate CRC-32 value of an uploaded file.
    """
    file_data = uploaded_file.getvalue()

    crc_value = zlib.crc32(file_data) & 0xFFFFFFFF

    return f"{crc_value:08X}"


# --------------------------------------------------
# FILE UPLOAD SECTION
# --------------------------------------------------

st.header("📂 Select Files")

col1, col2 = st.columns(2)

# --------------------------------------------------
# ORIGINAL / INPUT FILE
# --------------------------------------------------

with col1:

    st.subheader("📌 Original / Input File")

    original_file = st.file_uploader(
        "Upload the original file",
        type=[
            "txt",
            "csv",
            "pdf",
            "jpg",
            "jpeg",
            "png"
        ],
        key="original_file"
    )

# --------------------------------------------------
# CURRENT FILE
# --------------------------------------------------

with col2:

    st.subheader("📌 Current File")

    current_file = st.file_uploader(
        "Upload the current file",
        type=[
            "txt",
            "csv",
            "pdf",
            "jpg",
            "jpeg",
            "png"
        ],
        key="current_file"
    )


# --------------------------------------------------
# CHECK WHETHER BOTH FILES ARE UPLOADED
# --------------------------------------------------

if original_file is not None and current_file is not None:

    st.divider()

    st.header("🔍 File Information")

    # --------------------------------------------------
    # FILE INFORMATION
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Original / Input File")

        st.write("**File Name:**", original_file.name)

        original_size = len(original_file.getvalue())

        st.write(
            "**File Size:**",
            f"{original_size:,} bytes"
        )

    with col2:

        st.subheader("Current File")

        st.write("**File Name:**", current_file.name)

        current_size = len(current_file.getvalue())

        st.write(
            "**File Size:**",
            f"{current_size:,} bytes"
        )

    # --------------------------------------------------
    # CALCULATE CRC-32
    # --------------------------------------------------

    original_crc = calculate_crc32(original_file)

    current_crc = calculate_crc32(current_file)

    # --------------------------------------------------
    # DISPLAY CRC VALUES
    # --------------------------------------------------

    st.divider()

    st.header("🔢 CRC-32 Values")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Original / Input File")

        st.code(
            original_crc,
            language="text"
        )

    with col2:

        st.subheader("Current File")

        st.code(
            current_crc,
            language="text"
        )

    # --------------------------------------------------
    # COMPARE CRC VALUES
    # --------------------------------------------------

    st.divider()

    st.header("🛡️ Integrity Verification")

    if original_crc == current_crc:

        st.success(
            "✅ FILE INTEGRITY VERIFIED"
        )

        st.write(
            "The CRC-32 values are identical. "
            "The current file contents match the original file contents."
        )

    else:

        st.error(
            "❌ FILE MODIFIED OR CORRUPTED"
        )

        st.write(
            "The CRC-32 values are different. "
            "The current file contents do not match the original file."
        )

    # --------------------------------------------------
    # COMPARISON TABLE
    # --------------------------------------------------

    st.divider()

    st.subheader("📊 Comparison Summary")

    comparison_data = {
        "Property": [
            "File Name",
            "File Size",
            "CRC-32"
        ],

        "Original / Input File": [
            original_file.name,
            f"{original_size:,} bytes",
            original_crc
        ],

        "Current File": [
            current_file.name,
            f"{current_size:,} bytes",
            current_crc
        ]
    }

    st.table(comparison_data)

else:

    st.warning(
        "⬆️ Please upload both the Original/Input File "
        "and the Current File to perform verification."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "CRC-32 Based File Integrity Checker | "
    "Used to detect accidental changes in file contents"
)
