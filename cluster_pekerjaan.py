import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from itertools import combinations

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

# Fungsi bantuan
def convert_df_to_csv(df):
    """Convert dataframe to CSV for download"""
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

# Load data
df_kbli_cluster, df_kbli_full, df_tidak_terklasifikasi, df_cluster_pekerjaan = load_data()

if df_kbli_cluster is None:
    st.stop()

# DEBUG: Tampilkan informasi detail tentang data dalam expander yang collapsed
with st.sidebar.expander("🔍 Debug Info", expanded=False):
    st.write("**Data Overview:**")
    st.write(f"Total rows in df_kbli_cluster: {len(df_kbli_cluster)}")
    st.write(f"Unique KBLI codes: {df_kbli_cluster['KODE_KBLI'].nunique()}")
    st.write(f"Null values in KODE_KBLI: {df_kbli_cluster['KODE_KBLI'].isnull().sum()}")
    
    # Tampilkan duplikat KBLI jika ada
    kbli_counts = df_kbli_cluster['KODE_KBLI'].value_counts()
    duplicates = kbli_counts[kbli_counts > 1]
    if len(duplicates) > 0:
        st.write(f"**KBLI dengan duplikat:** {len(duplicates)}")
        for kbli, count in duplicates.head(10).items():  # Tampilkan max 10 duplikat
            st.write(f"  - {kbli}: {count} kali")
    
    # Info kolom
    st.write("**Columns in df_kbli_cluster:**")
    st.write(list(df_kbli_cluster.columns))
    
    # Sample data
    st.write("**Sample Data (first 5 rows):**")
    st.write(df_kbli_cluster[['KODE_KBLI', 'JUDUL_KBLI', 'CLUSTER']].head())

# Info Data di kanan atas - DIPERBAIKI dengan tambahan KBLI Multi Cluster
col_info1, col_info2, col_info3, col_info4, col_info5 = st.columns(5)

with col_info1:
    # Bersihkan data sebelum menghitung
    df_clean = df_kbli_cluster.dropna(subset=['KODE_KBLI']).copy()
    df_clean['KODE_KBLI'] = df_clean['KODE_KBLI'].astype(str).str.strip()
    
    # Hitung unique KBLI setelah cleaning
    unique_kbli_count = df_clean['KODE_KBLI'].nunique()
    st.metric("Total KBLI dalam cluster", unique_kbli_count)

with col_info2:
    st.metric("Total KBLI lengkap", len(df_kbli_full))

with col_info3:
    if df_cluster_pekerjaan is not None:
        st.metric("Total Pekerjaan UMKM", len(df_cluster_pekerjaan))

with col_info4:
    # Hitung KBLI yang hanya ada di 1 cluster
    kbli_counts = df_clean['KODE_KBLI'].value_counts()
    single_cluster_kbli = len(kbli_counts[kbli_counts == 1])
    st.metric("KBLI Single Cluster", single_cluster_kbli)

with col_info5:
    # Hitung KBLI Multi Cluster - DITAMBAHKAN
    multi_cluster_kbli = len(kbli_counts[kbli_counts > 1])
    st.metric("KBLI Multi Cluster", multi_cluster_kbli)

st.markdown("---")

# Tab untuk berbagai jenis data
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 KBLI Berdasarkan Cluster", 
    "📋 List Pekerjaan UMKM",
    "❓ Tidak Terklasifikasi", 
    "🔍 Pencarian KBLI",
    "🔄 KBLI Multi-Cluster",
    "✅ KBLI Single Cluster"
])

with tab1:
    st.header("KBLI Berdasarkan Cluster")
    
    # Gunakan data yang sudah dibersihkan
    available_clusters = df_clean['CLUSTER'].unique()
    
    # Filter Pilih Cluster
    col_filter1, col_filter2 = st.columns([1, 3])
    
    with col_filter1:
        selected_cluster = st.selectbox(
            "Pilih Cluster:",
            options=available_clusters,
            index=0,
            key="cluster_filter_tab1"
        )
    
    st.subheader(f"KBLI - Cluster: {selected_cluster}")
    
    # Filter data berdasarkan cluster yang dipilih
    filtered_data = df_clean[df_clean['CLUSTER'] == selected_cluster]
    
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
            else:
                st.info("Tidak ada data yang berhasil ditemukan")
        
        with col2:
            st.subheader("❌ Tidak Ditemukan")
            if len(df_tidak_ditemukan) > 0:
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
                    cluster_info = df_clean[
                        df_clean['KODE_KBLI'] == row['KODE KBLI']
                    ]['CLUSTER'].values
                    
                    if len(cluster_info) > 0:
                        st.write(f"**Cluster:** {cluster_info[0]}")
                    else:
                        st.write("**Cluster:** Tidak terkategorisasi")
        else:
            st.warning(f"Tidak ditemukan hasil untuk '{search_term}'")

with tab5:
    # Analisis data untuk menemukan KBLI multi-cluster
    @st.cache_data
    def find_multi_cluster_kbli(df_clean):
        """Mencari KBLI yang muncul di lebih dari 1 cluster"""
        # Hitung frekuensi setiap KBLI
        kbli_counts = df_clean['KODE_KBLI'].value_counts()
        
        # Ambil KBLI yang muncul lebih dari 1 kali
        multi_cluster_kbli = kbli_counts[kbli_counts > 1].index.tolist()
        
        # Kumpulkan data detail
        multi_cluster_data = []
        for kbli in multi_cluster_kbli:
            clusters = df_clean[df_clean['KODE_KBLI'] == kbli]['CLUSTER'].tolist()
            judul = df_clean[df_clean['KODE_KBLI'] == kbli]['JUDUL_KBLI'].iloc[0]
            
            multi_cluster_data.append({
                'KODE_KBLI': kbli,
                'JUDUL_KBLI': judul,
                'CLUSTERS': clusters,
                'JUMLAH_CLUSTER': len(clusters),
                'DETAIL_CLUSTER': ', '.join(clusters)
            })
        
        return pd.DataFrame(multi_cluster_data)
    
    # Cari data multi-cluster
    df_multi_cluster = find_multi_cluster_kbli(df_clean)
    
    st.header(f"🔄 KBLI Multi-Cluster ({len(df_multi_cluster)} KBLI)")
    
    if len(df_multi_cluster) > 0:
        # METRICS UTAMA
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total KBLI Multi-Cluster", len(df_multi_cluster))
        with col2:
            max_clusters = df_multi_cluster['JUMLAH_CLUSTER'].max()
            st.metric("Cluster Terbanyak per KBLI", max_clusters)
        with col3:
            avg_clusters = df_multi_cluster['JUMLAH_CLUSTER'].mean()
            st.metric("Rata-rata Cluster", f"{avg_clusters:.1f}")
        with col4:
            total_occurrences = df_multi_cluster['JUMLAH_CLUSTER'].sum()
            st.metric("Total Kemunculan", total_occurrences)
        
        st.markdown("---")
        
        # FILTER DAN PENCARIAN
        col_search, col_filter = st.columns([2, 1])
        
        with col_search:
            search_multi = st.text_input("Cari KBLI Multi-Cluster:", 
                                       placeholder="Masukkan kode atau judul KBLI...",
                                       key="search_multi")
        
        with col_filter:
            cluster_count_filter = st.selectbox("Filter Jumlah Cluster:",
                                              options=["Semua", "2 Cluster", "3 Cluster", "4+ Cluster"],
                                              key="cluster_count_filter")
        
        # Filter data
        filtered_multi = df_multi_cluster.copy()
        
        if search_multi:
            filtered_multi = filtered_multi[
                filtered_multi['KODE_KBLI'].str.contains(search_multi, case=False, na=False) |
                filtered_multi['JUDUL_KBLI'].str.contains(search_multi, case=False, na=False)
            ]
        
        if cluster_count_filter != "Semua":
            if cluster_count_filter == "2 Cluster":
                filtered_multi = filtered_multi[filtered_multi['JUMLAH_CLUSTER'] == 2]
            elif cluster_count_filter == "3 Cluster":
                filtered_multi = filtered_multi[filtered_multi['JUMLAH_CLUSTER'] == 3]
            else:  # 4+ Cluster
                filtered_multi = filtered_multi[filtered_multi['JUMLAH_CLUSTER'] >= 4]
        
        # VISUALISASI 1: Distribusi Jumlah Cluster - DIPERBAIKI
        st.subheader("📊 Distribusi KBLI Multi-Cluster")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Chart batang untuk distribusi jumlah cluster
            cluster_dist = df_multi_cluster['JUMLAH_CLUSTER'].value_counts().sort_index()
            
            fig_dist = px.bar(
                x=cluster_dist.index,
                y=cluster_dist.values,
                title="Distribusi Jumlah Cluster per KBLI",
                labels={'x': 'Jumlah Cluster', 'y': 'Jumlah KBLI'},
                color=cluster_dist.values,
                color_continuous_scale='viridis'
            )
            # HILANGKAN SKALA DESIMAL - DIPERBAIKI
            fig_dist.update_layout(
                showlegend=False,
                xaxis=dict(tickmode='linear', dtick=1),  # Pastikan angka bulat
                yaxis=dict(tickformat='d')  # Format integer untuk y-axis
            )
            # Tambahkan annotation untuk setiap bar
            fig_dist.update_traces(
                text=cluster_dist.values,
                textposition='outside',
                hovertemplate='<b>%{x} Cluster</b><br>Jumlah KBLI: %{y}<extra></extra>'
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with viz_col2:
            # Pie chart untuk persentase
            fig_pie = px.pie(
                values=cluster_dist.values,
                names=cluster_dist.index.astype(str) + ' Cluster',
                title="Persentase KBLI Multi-Cluster",
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # VISUALISASI 2: Cluster yang Sering Muncul Bersama
        st.subheader("🔗 Analisis Kombinasi Cluster")

        # Analisis kombinasi cluster
        def analyze_cluster_combinations(df_multi_cluster):
            """Menganalisis kombinasi cluster yang sering muncul bersama"""
            cluster_pairs = []
            
            for clusters in df_multi_cluster['CLUSTERS']:
                if len(clusters) >= 2:
                    # Generate semua pasangan cluster
                    pairs = list(combinations(sorted(clusters), 2))
                    cluster_pairs.extend(pairs)
            
            # Hitung frekuensi setiap pasangan
            pair_counter = Counter(cluster_pairs)
            
            # Ambil semua pasangan, tidak hanya 10 teratas
            all_pairs = pair_counter.most_common()
            
            return all_pairs

        top_cluster_pairs = analyze_cluster_combinations(df_multi_cluster)

        if top_cluster_pairs:
            pairs_df = pd.DataFrame(top_cluster_pairs, columns=['Cluster Pair', 'Jumlah_Pasangan'])
            pairs_df['Cluster Pair'] = pairs_df['Cluster Pair'].apply(lambda x: f"{x[0]} & {x[1]}")
            
            # Tampilkan total pairs
            st.metric("Total Kombinasi Cluster Pair", len(pairs_df))
            
            fig_pairs = px.bar(
                pairs_df,
                x='Jumlah_Pasangan',
                y='Cluster Pair',
                orientation='h',
                title=f"Kombinasi Cluster Pair ({len(pairs_df)} Total Pasangan)",
                color='Jumlah_Pasangan',
                color_continuous_scale='plasma',
                labels={'Jumlah_Pasangan': 'Jumlah Kemunculan'}
            )
            # HILANGKAN SKALA DESIMAL - DIPERBAIKI
            fig_pairs.update_layout(
                yaxis={'categoryorder':'total ascending'},
                xaxis=dict(tickformat='d')  # Format integer untuk x-axis
            )
            st.plotly_chart(fig_pairs, use_container_width=True)
            
            # Tampilkan tabel detail pairs
            with st.expander("📋 Detail Semua Cluster Pair"):
                st.dataframe(
                    pairs_df.rename(columns={'Jumlah_Pasangan': 'Jumlah Kemunculan'}),
                    use_container_width=True,
                    height=400
                )
        
        # TABEL DATA DETAIL
        st.subheader("📋 Detail KBLI Multi-Cluster")
        
        st.info(f"Menampilkan {len(filtered_multi)} dari {len(df_multi_cluster)} KBLI multi-cluster")
        
        # Tampilkan data dalam tabel expandable
        for idx, row in filtered_multi.iterrows():
            with st.expander(f"**{row['KODE_KBLI']}** - {row['JUDUL_KBLI']} ({row['JUMLAH_CLUSTER']} Cluster)", expanded=False):
                
                col_detail1, col_detail2 = st.columns(2)
                
                with col_detail1:
                    st.write("**Cluster Assignments:**")
                    for i, cluster in enumerate(row['CLUSTERS'], 1):
                        st.write(f"{i}. {cluster}")
                
                with col_detail2:
                    # Cari deskripsi lengkap
                    deskripsi = df_kbli_full[
                        df_kbli_full['KODE KBLI'] == row['KODE_KBLI']
                    ]['DESKRIPSI KBLI'].values
                    
                    if len(deskripsi) > 0 and pd.notna(deskripsi[0]):
                        st.write("**Deskripsi KBLI:**")
                        st.write(deskripsi[0])
                    else:
                        st.write("**Deskripsi:** Tidak tersedia")
                
                # Tampilkan warning untuk konflik
                if row['JUMLAH_CLUSTER'] >= 3:
                    st.warning("⚠️ KBLI ini memiliki 3 atau lebih cluster assignment. Perlu pengecekan ulang.")
        
        # DOWNLOAD DATA
        st.markdown("---")
        st.subheader("📥 Export Data")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            # Download data multi-cluster
            csv_multi = convert_df_to_csv(filtered_multi[['KODE_KBLI', 'JUDUL_KBLI', 'JUMLAH_CLUSTER', 'DETAIL_CLUSTER']])
            st.download_button(
                label="Download Data Multi-Cluster (CSV)",
                data=csv_multi,
                file_name="kbli_multi_cluster.csv",
                mime="text/csv",
                key="download_multi"
            )
        
        with col_export2:
            # Download data lengkap
            csv_full = convert_df_to_csv(filtered_multi)
            st.download_button(
                label="Download Data Lengkap (CSV)",
                data=csv_full,
                file_name="kbli_multi_cluster_lengkap.csv",
                mime="text/csv",
                key="download_full"
            )
        
    else:
        st.success("✅ Tidak ditemukan KBLI yang diclusterkan lebih dari 1 cluster")
        st.info("Semua KBLI memiliki assignment cluster yang unik")

with tab6:
    # Analisis data untuk menemukan KBLI single cluster
    @st.cache_data
    def find_single_cluster_kbli(df_clean):
        """Mencari KBLI yang hanya muncul di 1 cluster"""
        # Hitung frekuensi setiap KBLI
        kbli_counts = df_clean['KODE_KBLI'].value_counts()
        
        # Ambil KBLI yang muncul hanya 1 kali
        single_cluster_kbli = kbli_counts[kbli_counts == 1].index.tolist()
        
        # Kumpulkan data detail
        single_cluster_data = []
        for kbli in single_cluster_kbli:
            cluster_row = df_clean[df_clean['KODE_KBLI'] == kbli].iloc[0]
            
            single_cluster_data.append({
                'KODE_KBLI': kbli,
                'JUDUL_KBLI': cluster_row['JUDUL_KBLI'],
                'CLUSTER': cluster_row['CLUSTER'],
                'KETERANGAN': 'Single Cluster'
            })
        
        return pd.DataFrame(single_cluster_data)
    
    # Cari data single cluster
    df_single_cluster = find_single_cluster_kbli(df_clean)
    
    st.header(f"✅ KBLI Single Cluster ({len(df_single_cluster)} KBLI)")
    
    if len(df_single_cluster) > 0:
        # METRICS UTAMA
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total KBLI Single Cluster", len(df_single_cluster))
        with col2:
            percentage_single = (len(df_single_cluster) / df_clean['KODE_KBLI'].nunique()) * 100
            st.metric("Persentase dari Total", f"{percentage_single:.1f}%")
        with col3:
            unique_clusters = df_single_cluster['CLUSTER'].nunique()
            st.metric("Jumlah Cluster Unik", unique_clusters)
        
        st.markdown("---")
        
        # FILTER DAN PENCARIAN
        col_search, col_filter = st.columns([2, 1])
        
        with col_search:
            search_single = st.text_input("Cari KBLI Single Cluster:", 
                                        placeholder="Masukkan kode atau judul KBLI...",
                                        key="search_single")
        
        with col_filter:
            cluster_filter = st.selectbox("Filter Cluster:",
                                        options=["Semua"] + sorted(df_single_cluster['CLUSTER'].unique()),
                                        key="cluster_filter_single")
        
        # Filter data
        filtered_single = df_single_cluster.copy()
        
        if search_single:
            filtered_single = filtered_single[
                filtered_single['KODE_KBLI'].str.contains(search_single, case=False, na=False) |
                filtered_single['JUDUL_KBLI'].str.contains(search_single, case=False, na=False)
            ]
        
        if cluster_filter != "Semua":
            filtered_single = filtered_single[filtered_single['CLUSTER'] == cluster_filter]
        
        # VISUALISASI: Distribusi per Cluster - DIPERBAIKI
        st.subheader("📊 Distribusi KBLI Single Cluster per Cluster")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Chart batang untuk distribusi per cluster
            cluster_dist_single = filtered_single['CLUSTER'].value_counts()
            
            fig_dist_single = px.bar(
                x=cluster_dist_single.index,
                y=cluster_dist_single.values,
                title="Distribusi KBLI Single Cluster per Cluster",
                labels={'x': 'Cluster', 'y': 'Jumlah KBLI'},
                color=cluster_dist_single.values,
                color_continuous_scale='blues'
            )
            # HILANGKAN SKALA DESIMAL - DIPERBAIKI
            fig_dist_single.update_layout(
                showlegend=False,
                xaxis_tickangle=-45,
                yaxis=dict(tickformat='d')  # Format integer untuk y-axis
            )
            # Tambahkan annotation untuk setiap bar
            fig_dist_single.update_traces(
                text=cluster_dist_single.values,
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Jumlah KBLI: %{y}<extra></extra>'
            )
            st.plotly_chart(fig_dist_single, use_container_width=True)
        
        with viz_col2:
            # Pie chart untuk persentase
            if len(cluster_dist_single) > 0:
                fig_pie_single = px.pie(
                    values=cluster_dist_single.values,
                    names=cluster_dist_single.index,
                    title="Persentase KBLI Single Cluster per Cluster",
                    hole=0.4
                )
                st.plotly_chart(fig_pie_single, use_container_width=True)
        
        # TABEL DATA DETAIL
        st.subheader("📋 Detail KBLI Single Cluster")
        
        st.info(f"Menampilkan {len(filtered_single)} dari {len(df_single_cluster)} KBLI single cluster")
        
        # Tampilkan data dalam tabel expandable
        for idx, row in filtered_single.iterrows():
            with st.expander(f"**{row['KODE_KBLI']}** - {row['JUDUL_KBLI']}", expanded=False):
                
                col_detail1, col_detail2 = st.columns(2)
                
                with col_detail1:
                    st.write(f"**Cluster:** {row['CLUSTER']}")
                    st.write(f"**Status:** {row['KETERANGAN']}")
                
                with col_detail2:
                    # Cari deskripsi lengkap
                    deskripsi = df_kbli_full[
                        df_kbli_full['KODE KBLI'] == row['KODE_KBLI']
                    ]['DESKRIPSI KBLI'].values
                    
                    if len(deskripsi) > 0 and pd.notna(deskripsi[0]):
                        st.write("**Deskripsi KBLI:**")
                        st.write(deskripsi[0])
                    else:
                        st.write("**Deskripsi:** Tidak tersedia")
        
        # DOWNLOAD DATA
        st.markdown("---")
        st.subheader("📥 Export Data")
        
        csv_single = convert_df_to_csv(filtered_single[['KODE_KBLI', 'JUDUL_KBLI', 'CLUSTER']])
        st.download_button(
            label="Download Data Single Cluster (CSV)",
            data=csv_single,
            file_name="kbli_single_cluster.csv",
            mime="text/csv",
            key="download_single"
        )
        
    else:
        st.warning("Tidak ditemukan KBLI yang hanya di 1 cluster")
        st.info("Semua KBLI memiliki multiple cluster assignments")

# Footer
st.markdown("---")
st.markdown("**Dashboard KBLI Cluster** - Menampilkan klasifikasi KBLI berdasarkan cluster dan pekerjaan tidak terklasifikasi")
