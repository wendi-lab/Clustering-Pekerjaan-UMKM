import streamlit as st
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(
    page_title="KBLI Cluster Dashboard",
    page_icon="📊",
    layout="wide"
)

# Judul dashboard
st.title("📊 Dashboard Klasifikasi KBLI Berdasarkan Cluster")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    try:
        # Load data KBLI dari file utama
        df_kbli_cluster = pd.read_excel('20251022.xlsx', sheet_name='KBLI berdasarkan Cluster')
        
        # Load data KBLI lengkap untuk referensi deskripsi
        df_kbli_full = pd.read_excel('20251022.xlsx', sheet_name='KBLI')
        
        # Load data tidak terklasifikasi
        df_tidak_terklasifikasi = pd.read_excel('hasil_klasifikasi_kbli.xlsx', sheet_name='Hasil Klasifikasi')
        
        # Load data Cluster Pekerjaan
        df_cluster_pekerjaan = pd.read_excel('20251022.xlsx', sheet_name='Cluster Pekerjaan')
        
        return df_kbli_cluster, df_kbli_full, df_tidak_terklasifikasi, df_cluster_pekerjaan
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

# Load data
df_kbli_cluster, df_kbli_full, df_tidak_terklasifikasi, df_cluster_pekerjaan = load_data()

if df_kbli_cluster is None:
    st.stop()

# Info Data di kanan atas - DITAMBAHKAN
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("Total KBLI dalam cluster", len(df_kbli_cluster))
with col_info2:
    st.metric("Total KBLI lengkap", len(df_kbli_full))
with col_info3:
    if df_cluster_pekerjaan is not None:
        st.metric("Total Pekerjaan UMKM", len(df_cluster_pekerjaan))

st.markdown("---")

# Tab untuk berbagai jenis data
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 KBLI Berdasarkan Cluster", 
    "📋 List Pekerjaan UMKM",
    "❓ Tidak Terklasifikasi", 
    "🔍 Pencarian KBLI"
])

with tab1:
    st.header("KBLI Berdasarkan Cluster")
    
    # Filter Pilih Cluster
    col_filter1, col_filter2 = st.columns([1, 3])
    
    with col_filter1:
        available_clusters = df_kbli_cluster['CLUSTER'].unique()
        selected_cluster = st.selectbox(
            "Pilih Cluster:",
            options=available_clusters,
            index=0,
            key="cluster_filter_tab1"
        )
    
    st.subheader(f"KBLI - Cluster: {selected_cluster}")
    
    # Filter data berdasarkan cluster yang dipilih
    filtered_data = df_kbli_cluster[df_kbli_cluster['CLUSTER'] == selected_cluster]
    
    if len(filtered_data) > 0:
        # Tampilkan data dalam bentuk tabel
        for idx, row in filtered_data.iterrows():
            with st.expander(f"**{row['KODE_KBLI']}** - {row['JUDUL_KBLI']}", expanded=False):
                # Cari deskripsi lengkap dari data KBLI
                deskripsi = df_kbli_full[
                    df_kbli_full['KODE KBLI'] == row['KODE_KBLI']
                ]['DESKRIPSI KBLI'].values
                
                if len(deskripsi) > 0 and pd.notna(deskripsi[0]):
                    st.write(f"**Deskripsi:** {deskripsi[0]}")
                else:
                    st.write("**Deskripsi:** Tidak tersedia")
                # INFO CLUSTER DAN KODE KBLI DIHAPUS KARENA REDUNDANT
        
        # Tampilkan summary
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Jumlah Kode KBLI", len(filtered_data))
        with col2:
            st.metric("Total Cluster", len(available_clusters))
    else:
        st.info("Tidak ada data untuk cluster yang dipilih")

with tab2:
    st.header("📋 List Pekerjaan UMKM dan Cluster")
    
    if df_cluster_pekerjaan is not None:
        # Filter Pilih Cluster untuk tab ini
        col_filter1, col_filter2 = st.columns([1, 3])
        
        with col_filter1:
            available_clusters_pekerjaan = df_cluster_pekerjaan['CLUSTER'].unique()
            selected_cluster_pekerjaan = st.selectbox(
                "Pilih Cluster:",
                options=available_clusters_pekerjaan,
                index=0,
                key="cluster_filter_tab2"
            )
        
        st.subheader(f"Pekerjaan UMKM - Cluster: {selected_cluster_pekerjaan}")
        
        # Filter data berdasarkan cluster yang dipilih
        filtered_pekerjaan = df_cluster_pekerjaan[df_cluster_pekerjaan['CLUSTER'] == selected_cluster_pekerjaan]
        
        if len(filtered_pekerjaan) > 0:
            # Tampilkan dalam bentuk list sederhana
            st.write(f"**Jumlah Pekerjaan:** {len(filtered_pekerjaan)}")
            
            # Tampilkan dalam bentuk bullet list
            for idx, row in filtered_pekerjaan.iterrows():
                st.write(f"• {row['List Pekerjaan UMKM']}")
            
            # Tampilkan summary
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Pekerjaan", len(filtered_pekerjaan))
            with col2:
                st.metric("Total Cluster", len(available_clusters_pekerjaan))
            with col3:
                # Hitung persentase dari total
                total_pekerjaan = len(df_cluster_pekerjaan)
                percentage = (len(filtered_pekerjaan) / total_pekerjaan) * 100
                st.metric("Persentase", f"{percentage:.1f}%")
            
            # Tampilkan juga dalam tabel ringkas
            st.subheader("Tabel Ringkas")
            st.dataframe(
                filtered_pekerjaan[['List Pekerjaan UMKM', 'CLUSTER']],
                use_container_width=True,
                height=300
            )
        else:
            st.info("Tidak ada data pekerjaan untuk cluster yang dipilih")
        
        # Statistik overall
        st.markdown("---")
        st.subheader("📊 Statistik Keseluruhan")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Pekerjaan UMKM", len(df_cluster_pekerjaan))
        with col2:
            st.metric("Total Cluster", len(available_clusters_pekerjaan))
        with col3:
            # Hitung pekerjaan tidak terklasifikasi
            tidak_terklasifikasi = len(df_cluster_pekerjaan[df_cluster_pekerjaan['CLUSTER'] == 'Tidak Terklasifikasi'])
            st.metric("Tidak Terklasifikasi", tidak_terklasifikasi)
        with col4:
            # Hitung persentase terklasifikasi
            terklasifikasi = len(df_cluster_pekerjaan) - tidak_terklasifikasi
            percentage_terklasifikasi = (terklasifikasi / len(df_cluster_pekerjaan)) * 100
            st.metric("Tingkat Klasifikasi", f"{percentage_terklasifikasi:.1f}%")
        
    else:
        st.error("Data Cluster Pekerjaan tidak dapat dimuat")

with tab3:
    st.header("Pekerjaan Tidak Terklasifikasi")
    
    if df_tidak_terklasifikasi is not None:
        # Pisahkan data yang ditemukan dan tidak ditemukan
        df_ditemukan = df_tidak_terklasifikasi[df_tidak_terklasifikasi['KODE KBLI'] != 'Tidak Ditemukan']
        df_tidak_ditemukan = df_tidak_terklasifikasi[df_tidak_terklasifikasi['KODE KBLI'] == 'Tidak Ditemukan']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Berhasil Ditemukan")
            if len(df_ditemukan) > 0:
                for idx, row in df_ditemukan.iterrows():
                    with st.expander(f"**{row['KODE KBLI']}** - {row['JUDUL KBLI']}", expanded=False):
                        # HANYA TAMPILKAN PEKERJAAN UMKM DAN DESKRIPSI KBLI
                        st.write(f"**Pekerjaan UMKM:** {row['List Pekerjaan UMKM']}")
                        st.write(f"**Deskripsi KBLI:** {row['DESKRIPSI KBLI']}")
                        # TINGKAT KECOCOKAN DAN KETERANGAN DIHAPUS
            else:
                st.info("Tidak ada data yang berhasil ditemukan")
        
        with col2:
            st.subheader("❌ Tidak Ditemukan")
            if len(df_tidak_ditemukan) > 0:
                # TAMPILKAN LANGSUNG TANPA EXPANDABLE - DIUBAH
                for idx, row in df_tidak_ditemukan.iterrows():
                    st.write(f"• **{row['List Pekerjaan UMKM']}**")
                    st.write(f"  Status: {row['KODE KBLI']} | Cluster: {row['CLUSTER']}")
                    st.write("  *Perlu klasifikasi manual*")
                    st.write("---")
            else:
                st.info("Tidak ada data yang tidak ditemukan")
        
        # Summary metrics
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tidak Terklasifikasi", len(df_tidak_terklasifikasi))
        with col2:
            st.metric("Berhasil Ditemukan", len(df_ditemukan))
        with col3:
            st.metric("Tidak Ditemukan", len(df_tidak_ditemukan))
        with col4:
            success_rate = (len(df_ditemukan) / len(df_tidak_terklasifikasi)) * 100 if len(df_tidak_terklasifikasi) > 0 else 0
            st.metric("Tingkat Keberhasilan", f"{success_rate:.1f}%")
    else:
        st.error("Data tidak terklasifikasi tidak dapat dimuat")

with tab4:
    st.header("🔍 Pencarian KBLI")
    
    # Pencarian berdasarkan keyword
    search_term = st.text_input("Masukkan kata kunci pencarian (Kode KBLI atau Judul):")
    
    if search_term:
        # Search in KBLI full data
        search_results = df_kbli_full[
            df_kbli_full['KODE KBLI'].astype(str).str.contains(search_term, case=False, na=False) |
            df_kbli_full['JUDUL KBLI'].str.contains(search_term, case=False, na=False) |
            df_kbli_full['DESKRIPSI KBLI'].str.contains(search_term, case=False, na=False)
        ]
        
        if len(search_results) > 0:
            st.success(f"Ditemukan {len(search_results)} hasil pencarian untuk '{search_term}'")
            
            for idx, row in search_results.iterrows():
                with st.expander(f"**{row['KODE KBLI']}** - {row['JUDUL KBLI']}", expanded=False):
                    st.write(f"**Deskripsi:** {row['DESKRIPSI KBLI']}")
                    
                    # Cari cluster dari data cluster
                    cluster_info = df_kbli_cluster[
                        df_kbli_cluster['KODE_KBLI'] == row['KODE KBLI']
                    ]['CLUSTER'].values
                    
                    if len(cluster_info) > 0:
                        st.write(f"**Cluster:** {cluster_info[0]}")
                    else:
                        st.write("**Cluster:** Tidak terkategorisasi")
        else:
            st.warning(f"Tidak ditemukan hasil untuk '{search_term}'")

# Footer
st.markdown("---")
st.markdown("**Dashboard KBLI Cluster** - Menampilkan klasifikasi KBLI berdasarkan cluster dan pekerjaan tidak terklasifikasi")