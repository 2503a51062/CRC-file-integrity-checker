import streamlit as st
import os
import tempfile
import zlib


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CRC File Integrity Checker",
    page_icon="🔐",
    layout="wide"
)


# =========================================================
# CRC CONFIGURATION
# =========================================================

# CRC-3:
# Width  = 3
# Poly   = 0x3
# Init   = 0x0
#
# CRC-4/ITU:
# Width  = 4
# Poly   = 0x3
# Init   = 0x0
#
# CRC-8:
# Width  = 8
# Poly   = 0x07
# Init   = 0x00
#
# CRC-32/IEEE:
# Polynomial = 0xEDB88320 (reflected form)
# Init       = 0xFFFFFFFF
# XOROUT     = 0xFFFFFFFF


# =========================================================
# GENERATE FAST CRC TABLE
# =========================================================

def generate_crc_table(width, polynomial):
    """
    Generate a lookup table for CRC calculation.

    This table is created only once when the application starts.
    """

    table_size = 1 << width
    mask = table_size - 1

    table = [
        [0] * 256
        for _ in range(table_size)
    ]

    for crc in range(table_size):

        for byte in range(256):

            value = crc

            for bit in range(8):

                input_bit = (
                    byte >> (7 - bit)
                ) & 1

                top_bit = (
                    value >> (width - 1)
                ) & 1

                value = (
                    value << 1
                ) & mask

                if top_bit ^ input_bit:

                    value ^= polynomial

            table[crc][byte] = value

    return table


# =========================================================
# CREATE TABLES
# =========================================================

CRC3_TABLE = generate_crc_table(
    width=3,
    polynomial=0x3
)

CRC4_TABLE = generate_crc_table(
    width=4,
    polynomial=0x3
)

CRC8_TABLE = generate_crc_table(
    width=8,
    polynomial=0x07
)


# =========================================================
# FAST CRC CALCULATION
# =========================================================

def calculate_crc_values(
    file_path,
    progress_bar=None,
    status_text=None
):

    # Initial CRC values
    crc3 = 0x0
    crc4 = 0x0
    crc8 = 0x00

    # Standard CRC-32 initial value
    crc32 = 0xFFFFFFFF

    # File size
    file_size = os.path.getsize(file_path)

    processed = 0

    # 4 MB chunks
    chunk_size = 4 * 1024 * 1024


    # -----------------------------------------------------
    # OPEN FILE
    # -----------------------------------------------------

    with open(file_path, "rb") as file:

        while True:

            chunk = file.read(chunk_size)

            if not chunk:
                break


            # =================================================
            # CRC-3
            # =================================================

            for byte in chunk:

                crc3 = CRC3_TABLE[crc3][byte]


            # =================================================
            # CRC-4
            # =================================================

            for byte in chunk:

                crc4 = CRC4_TABLE[crc4][byte]


            # =================================================
            # CRC-8
            # =================================================

            for byte in chunk:

                crc8 = CRC8_TABLE[crc8][byte]


            # =================================================
            # CRC-32
            # =================================================

            # zlib uses the optimized CRC-32 implementation
            crc32 = zlib.crc32(
                chunk,
                crc32
            )


            # =================================================
            # UPDATE PROGRESS
            # =================================================

            processed += len(chunk)

            progress = (
                processed / file_size
                if file_size > 0
                else 1
            )

            if progress_bar is not None:

                progress_bar.progress(
                    min(progress, 1.0)
                )

            if status_text is not None:

                status_text.text(
                    f"Processing: "
                    f"{processed / (1024 * 1024):.2f} MB / "
                    f"{file_size / (1024 * 1024):.2f} MB"
                )


    # Final CRC-32 XOR
    crc32 = (
        crc32 ^ 0xFFFFFFFF
    ) & 0xFFFFFFFF


    return {
        "CRC-3": crc3,
        "CRC-4": crc4,
        "CRC-8": crc8,
        "CRC-32": crc32
    }


# =========================================================
# FILE SIZE FUNCTION
# =========================================================

def get_file_size(file_path):

    size = os.path.getsize(file_path)

    if size < 1024:

        return f"{size} Bytes"

    elif size < 1024 * 1024:

        return f"{size / 1024:.2f} KB"

    elif size < 1024 * 1024 * 1024:

        return (
            f"{size / (1024 * 1024):.2f} MB"
        )

    else:

        return (
            f"{size / (1024 * 1024 * 1024):.2f} GB"
        )


# =========================================================
# SAVE UPLOADED FILE
# =========================================================

def save_uploaded_file(uploaded_file):

    temp = tempfile.NamedTemporaryFile(
        delete=False
    )

    try:

        # Read in chunks
        while True:

            data = uploaded_file.read(
                4 * 1024 * 1024
            )

            if not data:
                break

            temp.write(data)

    finally:

        temp.close()

    return temp.name


# =========================================================
# FORMAT CRC
# =========================================================

def format_crc(algorithm, value):

    if algorithm == "CRC-3":

        return f"0x{value:01X}"

    elif algorithm == "CRC-4":

        return f"0x{value:01X}"

    elif algorithm == "CRC-8":

        return f"0x{value:02X}"

    elif algorithm == "CRC-32":

        return f"0x{value:08X}"

    return str(value)


# =========================================================
# TITLE
# =========================================================

st.title(
    "🔐 CRC File Integrity Checker"
)

st.write(
    "Compare an original file and a received file "
    "using CRC-3, CRC-4, CRC-8 and CRC-32."
)

st.divider()


# =========================================================
# FILE UPLOADERS
# =========================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "📁 Original File"
    )

    original_file = st.file_uploader(
        "Upload the original file",
        type=None,
        key="original"
    )


with col2:

    st.subheader(
        "📁 Received File"
    )

    received_file = st.file_uploader(
        "Upload the received file",
        type=None,
        key="received"
    )


# =========================================================
# CHECK BUTTON
# =========================================================

if (
    original_file is not None
    and received_file is not None
):

    st.divider()

    if st.button(
        "🔍 Check File Integrity",
        use_container_width=True
    ):

        original_path = None
        received_path = None


        try:

            # =================================================
            # SAVE FILES
            # =================================================

            with st.spinner(
                "Preparing files..."
            ):

                original_path = (
                    save_uploaded_file(
                        original_file
                    )
                )

                received_path = (
                    save_uploaded_file(
                        received_file
                    )
                )


            # =================================================
            # FILE INFORMATION
            # =================================================

            st.subheader(
                "📊 File Information"
            )

            info_col1, info_col2 = st.columns(2)


            with info_col1:

                st.write(
                    "### Original File"
                )

                st.write(
                    f"**Name:** "
                    f"{original_file.name}"
                )

                st.write(
                    f"**Size:** "
                    f"{get_file_size(original_path)}"
                )


            with info_col2:

                st.write(
                    "### Received File"
                )

                st.write(
                    f"**Name:** "
                    f"{received_file.name}"
                )

                st.write(
                    f"**Size:** "
                    f"{get_file_size(received_path)}"
                )


            # =================================================
            # SIZE CHECK
            # =================================================

            original_size = os.path.getsize(
                original_path
            )

            received_size = os.path.getsize(
                received_path
            )


            if original_size != received_size:

                st.warning(
                    "⚠️ File sizes are different."
                )

                st.write(
                    "The CRC values will still be calculated, "
                    "but the files cannot be identical."
                )


            # =================================================
            # ORIGINAL CRC CALCULATION
            # =================================================

            st.divider()

            st.subheader(
                "⚙️ Calculating Original File"
            )

            original_progress = st.progress(
                0
            )

            original_status = st.empty()


            original_crc = calculate_crc_values(
                original_path,
                original_progress,
                original_status
            )


            original_progress.progress(1.0)

            original_status.success(
                "✅ Original file calculation completed."
            )


            # =================================================
            # RECEIVED CRC CALCULATION
            # =================================================

            st.subheader(
                "⚙️ Calculating Received File"
            )

            received_progress = st.progress(
                0
            )

            received_status = st.empty()


            received_crc = calculate_crc_values(
                received_path,
                received_progress,
                received_status
            )


            received_progress.progress(1.0)

            received_status.success(
                "✅ Received file calculation completed."
            )


            # =================================================
            # RESULTS
            # =================================================

            st.divider()

            st.subheader(
                "🔢 CRC Integrity Results"
            )


            for algorithm in [
                "CRC-3",
                "CRC-4",
                "CRC-8",
                "CRC-32"
            ]:

                original_value = (
                    original_crc[algorithm]
                )

                received_value = (
                    received_crc[algorithm]
                )


                original_display = format_crc(
                    algorithm,
                    original_value
                )

                received_display = format_crc(
                    algorithm,
                    received_value
                )


                st.write(
                    f"### {algorithm}"
                )


                result_col1, result_col2, result_col3 = (
                    st.columns(3)
                )


                with result_col1:

                    st.write(
                        f"**Original:** "
                        f"`{original_display}`"
                    )


                with result_col2:

                    st.write(
                        f"**Received:** "
                        f"`{received_display}`"
                    )


                with result_col3:

                    if (
                        original_value
                        == received_value
                    ):

                        st.success(
                            "✅ MATCH"
                        )

                    else:

                        st.error(
                            "❌ CORRUPTED"
                        )


            # =================================================
            # FINAL RESULT
            # =================================================

            st.divider()

            all_match = all(
                original_crc[algorithm]
                == received_crc[algorithm]
                for algorithm in [
                    "CRC-3",
                    "CRC-4",
                    "CRC-8",
                    "CRC-32"
                ]
            )


            if (
                all_match
                and original_size == received_size
            ):

                st.success(
                    "✅ FILE INTEGRITY VERIFIED\n\n"
                    "The original and received files "
                    "have matching CRC values."
                )

                st.balloons()

            else:

                st.error(
                    "❌ FILE CORRUPTION DETECTED\n\n"
                    "The CRC values do not match."
                )


        except Exception as e:

            st.error(
                f"❌ Error: {str(e)}"
            )


        finally:

            # =================================================
            # DELETE TEMPORARY FILES
            # =================================================

            if original_path:

                try:
                    os.remove(
                        original_path
                    )
                except:
                    pass


            if received_path:

                try:
                    os.remove(
                        received_path
                    )
                except:
                    pass


# =========================================================
# CRC INFORMATION
# =========================================================

st.divider()

st.subheader(
    "ℹ️ CRC Algorithms"
)

st.write("""
**CRC-3**
- Width: 3 bits
- Polynomial: 0x3
- Initial value: 0x0

**CRC-4**
- Width: 4 bits
- Polynomial: 0x3
- Initial value: 0x0

**CRC-8**
- Width: 8 bits
- Polynomial: 0x07
- Initial value: 0x00

**CRC-32**
- Standard CRC-32/IEEE
- Polynomial: 0xEDB88320
- Initial value: 0xFFFFFFFF
- Final XOR: 0xFFFFFFFF
""")

st.info(
    "⚡ Optimized lookup-table CRC calculation is used "
    "for CRC-3, CRC-4 and CRC-8. CRC-32 uses Python's "
    "optimized zlib implementation. Files are processed "
    "in 4 MB chunks."
)
