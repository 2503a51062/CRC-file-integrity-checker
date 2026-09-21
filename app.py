import streamlit as st
import zlib

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="CRC-Based File Integrity Checker",
    page_icon="🔐",
    layout="wide"
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🔐 CRC-Based File Integrity Checker")

st.write(
    "Upload the original file and the current file to calculate "
    "CRC-3, CRC-4, CRC-8 and CRC-32 values and verify file integrity."
)

st.info(
    "Supported files: TXT, CSV, PDF, JPG, JPEG and PNG"
)

# --------------------------------------------------
# CRC GENERIC FUNCTION
# --------------------------------------------------

def crc_calculate(data, width, polynomial, init=0, xorout=0):
    """
    Generic non-reflected CRC calculation.
    """

    crc = init
    topbit = 1 << (width - 1)
    mask = (1 << width) - 1

    for byte in data:
        crc ^= byte << (width - 8)

        for _ in range(8):
            if crc & topbit:
                crc = ((crc << 1) ^ polynomial) & mask
            else:
                crc = (crc << 1) & mask

    return (crc ^ xorout) & mask


# --------------------------------------------------
# CRC FUNCTIONS
# --------------------------------------------------

def calculate_crc3(data):
    """
    CRC-3/GSM
    Polynomial: x^3 + x + 1
    Poly = 0x3
    """

    return crc_calculate(
        data,
        width=3,
        polynomial=0x3,
        init=0x0,
        xorout=0x0
    )


def calculate_crc4(data):
    """
    CRC-4/ITU
    Polynomial: x^4 + x + 1
    Poly = 0x3
    """

    return crc_calculate(
        data,
        width=4,
        polynomial=0x3,
        init=0x0,
        xorout=0x0
    )


def calculate_crc8(data):
    """
    CRC-8/SMBus
    Polynomial: x^8 + x^2 + x + 1
    Poly = 0x07
    """

    return crc_calculate(
        data,
        width=8,
        polynomial=0x07,
        init=0x00,
        xorout=0x00
    )


def calculate_crc32(data):
    """
    CRC-32/ISO-HDLC
    """

    return zlib.crc32(data) & 0xffffffff


# --------------------------------------------------
# CALCULATE ALL CRCS
# --------------------------------------------------

def calculate_all_crcs(file):

    data = file.getvalue()

    return {
        "CRC-3": calculate_crc3(data),
        "CRC-4": calculate_crc4(data),
        "CRC-8": calculate_crc8(data),
        "CRC-32": calculate_crc32(data)
    }


# --------------------------------------------------
# FILE UPLOAD SECTION
# --------------------------------------------------

st.header("📂 Upload Files")

col1, col2 = st.columns(2)

# ORIGINAL / INPUT FILE
with col1:

    st.subheader("📄 Original / Input File")

    original_file = st.file_uploader(
        "Choose the original file",
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


# CURRENT FILE
with col2:

    st.subheader("📄 Current File")

    current_file = st.file_uploader(
        "Choose the current file",
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
# PROCESS FILES
# --------------------------------------------------

if original_file is not None and current_file is not None:

    # Get CRC values
    original_crcs = calculate_all_crcs(original_file)
    current_crcs = calculate_all_crcs(current_file)

    # --------------------------------------------------
    # FILE INFORMATION
    # --------------------------------------------------

    st.divider()

    st.header("📋 File Information")

    info1, info2 = st.columns(2)

    with info1:

        st.subheader("Original / Input File")

        st.write(
            "**File Name:**",
            original_file.name
        )

        st.write(
            "**File Size:**",
            f"{len(original_file.getvalue()):,} bytes"
        )

    with info2:

        st.subheader("Current File")

        st.write(
            "**File Name:**",
            current_file.name
        )

        st.write(
            "**File Size:**",
            f"{len(current_file.getvalue()):,} bytes"
        )

    # --------------------------------------------------
    # CRC TABLE
    # --------------------------------------------------

    st.divider()

    st.header("🔢 CRC Values")

    st.write(
        "The following CRC algorithms are calculated for both files:"
    )

    # Header
    h1, h2, h3, h4 = st.columns(4)

    with h1:
        st.markdown("### CRC-3")

    with h2:
        st.markdown("### CRC-4")

    with h3:
        st.markdown("### CRC-8")

    with h4:
        st.markdown("### CRC-32")


    # Original values
    st.subheader("📄 Original / Input File")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.code(
            f"{original_crcs['CRC-3']:01X}",
            language="text"
        )

    with c2:
        st.code(
            f"{original_crcs['CRC-4']:01X}",
            language="text"
        )

    with c3:
        st.code(
            f"{original_crcs['CRC-8']:02X}",
            language="text"
        )

    with c4:
        st.code(
            f"{original_crcs['CRC-32']:08X}",
            language="text"
        )


    # Current values
    st.subheader("📄 Current File")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.code(
            f"{current_crcs['CRC-3']:01X}",
            language="text"
        )

    with c2:
        st.code(
            f"{current_crcs['CRC-4']:01X}",
            language="text"
        )

    with c3:
        st.code(
            f"{current_crcs['CRC-8']:02X}",
            language="text"
        )

    with c4:
        st.code(
            f"{current_crcs['CRC-32']:08X}",
            language="text"
        )


    # --------------------------------------------------
    # VERIFICATION
    # --------------------------------------------------

    st.divider()

    st.header("🛡️ Integrity Verification")

    # Individual comparisons
    crc3_match = (
        original_crcs["CRC-3"]
        == current_crcs["CRC-3"]
    )

    crc4_match = (
        original_crcs["CRC-4"]
        == current_crcs["CRC-4"]
    )

    crc8_match = (
        original_crcs["CRC-8"]
        == current_crcs["CRC-8"]
    )

    crc32_match = (
        original_crcs["CRC-32"]
        == current_crcs["CRC-32"]
    )


    # --------------------------------------------------
    # COMPARISON TABLE
    # --------------------------------------------------

    st.subheader("🔍 CRC Comparison")

    comparison_data = {
        "CRC Algorithm": [
            "CRC-3",
            "CRC-4",
            "CRC-8",
            "CRC-32"
        ],

        "Original": [
            f"{original_crcs['CRC-3']:01X}",
            f"{original_crcs['CRC-4']:01X}",
            f"{original_crcs['CRC-8']:02X}",
            f"{original_crcs['CRC-32']:08X}"
        ],

        "Current": [
            f"{current_crcs['CRC-3']:01X}",
            f"{current_crcs['CRC-4']:01X}",
            f"{current_crcs['CRC-8']:02X}",
            f"{current_crcs['CRC-32']:08X}"
        ],

        "Status": [
            "MATCH" if crc3_match else "DIFFERENT",
            "MATCH" if crc4_match else "DIFFERENT",
            "MATCH" if crc8_match else "DIFFERENT",
            "MATCH" if crc32_match else "DIFFERENT"
        ]
    }

    st.table(comparison_data)


    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    all_match = (
        crc3_match
        and crc4_match
        and crc8_match
        and crc32_match
    )

    if all_match:

        st.success(
            "✅ FILE INTEGRITY VERIFIED\n\n"
            "All four CRC values match. "
            "The current file has the same contents as the original file."
        )

    else:

        st.error(
            "❌ FILE MODIFIED / CORRUPTED\n\n"
            "One or more CRC values are different. "
            "The current file does not match the original file."
        )


# --------------------------------------------------
# NO FILE MESSAGE
# --------------------------------------------------

else:

    st.warning(
        "Please upload BOTH the Original / Input File "
        "and the Current File to calculate CRC values."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "CRC-Based File Integrity Checker | "
    "CRC-3 • CRC-4 • CRC-8 • CRC-32"
)
