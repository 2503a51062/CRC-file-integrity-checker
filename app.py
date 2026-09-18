import streamlit as st
import os


# ============================================================
# CRC CALCULATION FUNCTION
# ============================================================

def calculate_crc(data_bits, polynomial):
    """
    Calculate CRC using modulo-2 division.
    data_bits  : binary string
    polynomial : generator polynomial in binary form
    """

    degree = len(polynomial) - 1

    # Append zeros according to generator polynomial degree
    working_data = list(data_bits + "0" * degree)

    # Convert polynomial to list
    poly = list(polynomial)

    # Modulo-2 division using XOR
    for i in range(len(data_bits)):

        if working_data[i] == "1":

            for j in range(len(poly)):

                working_data[i + j] = str(
                    int(working_data[i + j]) ^
                    int(poly[j])
                )

    # CRC remainder
    remainder = "".join(working_data[-degree:])

    return remainder


# ============================================================
# TEXT TO BINARY
# ============================================================

def text_to_binary(text):
    """
    Convert text into binary using UTF-8 bytes.
    """

    byte_data = text.encode("utf-8")

    binary_data = "".join(
        format(byte, "08b")
        for byte in byte_data
    )

    return binary_data


# ============================================================
# FILE TO BINARY
# ============================================================

def file_to_binary(uploaded_file):
    """
    Read uploaded file as bytes and convert to binary.
    """

    file_bytes = uploaded_file.getvalue()

    binary_data = "".join(
        format(byte, "08b")
        for byte in file_bytes
    )

    return binary_data


# ============================================================
# VERIFY CODEWORD
# ============================================================

def verify_codeword(codeword, polynomial):
    """
    Receiver-side CRC verification.

    If remainder is all zeros:
        No error detected

    Otherwise:
        Error detected
    """

    working_data = list(codeword)
    poly = list(polynomial)

    degree = len(polynomial) - 1

    for i in range(len(codeword) - degree):

        if working_data[i] == "1":

            for j in range(len(poly)):

                working_data[i + j] = str(
                    int(working_data[i + j]) ^
                    int(poly[j])
                )

    remainder = "".join(working_data[-degree:])

    return remainder


# ============================================================
# FLIP A BIT
# ============================================================

def flip_bit(binary_string, position):

    bits = list(binary_string)

    if 0 <= position < len(bits):

        if bits[position] == "0":
            bits[position] = "1"

        else:
            bits[position] = "0"

    return "".join(bits)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CRC-Based File Integrity Checker",
    page_icon="🔐",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🔐 CRC-Based File Integrity Checker")

st.write(
    "This application calculates CRC values and verifies "
    "whether binary data, text, or files have been modified."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("CRC Configuration")

input_type = st.sidebar.selectbox(
    "Select Input Type",
    [
        "Binary Data",
        "Text",
        "File"
    ]
)


algorithm = st.sidebar.selectbox(
    "Select CRC Algorithm",
    [
        "CRC-3",
        "CRC-4",
        "CRC-8"
    ]
)


# ============================================================
# GENERATOR POLYNOMIALS
# ============================================================

polynomials = {

    "CRC-3": "1011",

    "CRC-4": "10011",

    "CRC-8": "100000111"
}


polynomial = polynomials[algorithm]


st.sidebar.info(
    f"Generator Polynomial: {polynomial}"
)


# ============================================================
# INPUT SECTION
# ============================================================

st.header("1. Input Data")


data_bits = ""
file_name = ""


# ------------------------------------------------------------
# BINARY INPUT
# ------------------------------------------------------------

if input_type == "Binary Data":

    binary_input = st.text_input(
        "Enter Binary Data",
        value="101101"
    )

    if binary_input:

        if set(binary_input).issubset({"0", "1"}):

            data_bits = binary_input

            st.success(
                "Valid binary input."
            )

        else:

            st.error(
                "Please enter only 0 and 1."
            )


# ------------------------------------------------------------
# TEXT INPUT
# ------------------------------------------------------------

elif input_type == "Text":

    text_input = st.text_area(
        "Enter Text",
        value="HELLO"
    )

    if text_input:

        data_bits = text_to_binary(text_input)

        st.write(
            f"Text converted to {len(data_bits)} binary bits."
        )

        with st.expander("View Binary Representation"):

            st.code(data_bits)


# ------------------------------------------------------------
# FILE INPUT
# ------------------------------------------------------------

elif input_type == "File":

    uploaded_file = st.file_uploader(
        "Upload TXT, CSV, PDF or Image File",
        type=[
            "txt",
            "csv",
            "pdf",
            "png",
            "jpg",
            "jpeg"
        ]
    )

    if uploaded_file is not None:

        file_name = uploaded_file.name

        data_bits = file_to_binary(uploaded_file)

        st.success(
            f"File '{file_name}' uploaded successfully."
        )

        st.write(
            f"File size: {len(uploaded_file.getvalue())} bytes"
        )

        st.write(
            f"Binary data size: {len(data_bits)} bits"
        )


# ============================================================
# CRC CALCULATION
# ============================================================

st.header("2. CRC Calculation")


if data_bits:

    if st.button(
        "Calculate CRC",
        type="primary"
    ):

        crc_value = calculate_crc(
            data_bits,
            polynomial
        )

        codeword = data_bits + crc_value

        st.session_state["data_bits"] = data_bits
        st.session_state["crc_value"] = crc_value
        st.session_state["codeword"] = codeword
        st.session_state["polynomial"] = polynomial

        st.success("CRC calculated successfully!")


# ============================================================
# DISPLAY CRC RESULT
# ============================================================

if "crc_value" in st.session_state:

    st.subheader("CRC Result")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "CRC Value",
            st.session_state["crc_value"]
        )

    with col2:

        st.metric(
            "CRC Length",
            len(st.session_state["crc_value"])
        )

    with col3:

        st.metric(
            "Algorithm",
            algorithm
        )

    st.write("### Generated Codeword")

    st.code(
        st.session_state["codeword"]
    )


# ============================================================
# VERIFICATION
# ============================================================

if "codeword" in st.session_state:

    st.header("3. File/Data Integrity Verification")

    st.write(
        "The receiver divides the received codeword by "
        "the same generator polynomial."
    )

    if st.button("Verify Original Data"):

        received_codeword = st.session_state["codeword"]

        verification_remainder = verify_codeword(
            received_codeword,
            st.session_state["polynomial"]
        )

        if set(verification_remainder) == {"0"}:

            st.success(
                f"✓ NO ERROR DETECTED\n\n"
                f"Remainder: {verification_remainder}"
            )

        else:

            st.error(
                f"✗ ERROR DETECTED\n\n"
                f"Remainder: {verification_remainder}"
            )


# ============================================================
# ERROR SIMULATION
# ============================================================

if "codeword" in st.session_state:

    st.header("4. Error Simulation")

    codeword = st.session_state["codeword"]

    st.write(
        f"Codeword length: {len(codeword)} bits"
    )

    bit_position = st.number_input(
        "Select bit position to modify",
        min_value=0,
        max_value=len(codeword) - 1,
        value=0,
        step=1
    )

    if st.button("Simulate Bit Error"):

        corrupted_codeword = flip_bit(
            codeword,
            bit_position
        )

        st.session_state["corrupted_codeword"] = (
            corrupted_codeword
        )

        st.write("### Original Codeword")

        st.code(codeword)

        st.write("### Corrupted Codeword")

        st.code(corrupted_codeword)

        remainder = verify_codeword(
            corrupted_codeword,
            st.session_state["polynomial"]
        )

        st.write(
            f"Verification Remainder: `{remainder}`"
        )

        if set(remainder) == {"0"}:

            st.warning(
                "No error detected."
            )

        else:

            st.error(
                "✗ ERROR DETECTED - Data has been modified!"
            )


# ============================================================
# PROJECT INFORMATION
# ============================================================

st.header("5. How the System Works")

st.markdown(
    """
    **User Input**
    
    ↓
    
    **Dashboard**
    
    ↓
    
    **Python Input Processing**
    
    ↓
    
    **Convert Text/File to Binary**
    
    ↓
    
    **Append Zeros**
    
    ↓
    
    **Modulo-2 Division using XOR**
    
    ↓
    
    **CRC Remainder**
    
    ↓
    
    **Generate Codeword**
    
    ↓
    
    **Receiver Verification**
    
    ↓
    
    **No Error / Error Detected**
    """
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "CRC-Based File Integrity Checker | "
    "Operating Systems & Computer Networks Project"
)