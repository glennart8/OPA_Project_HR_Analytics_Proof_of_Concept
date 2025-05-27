
# Bakgrund, textfärger i dataframe mm
def load_background_style():
    return """
    <style>
    .stApp {
        background-image:
            linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
            url("https://images.unsplash.com/photo-1589939705384-5185137a7f0f?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: cover;
        background-position: center;
    }

    p, span, div {
        color: #F7E7CE !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 20px;
    }
    
        /* Header styling */
    header.stAppHeader {
    background: transparent !important;
    }
    
    </style>
    """