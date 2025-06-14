import streamlit as st
import json
import os
from datetime import datetime

# Configuração inicial
DB_FILE = "database.json"
st.set_page_config(page_title="Sistema de Atendimentos", layout="wide")

# Carregar ou inicializar o banco de dados
def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    return {
        "atendimentos": [],
        "consultores": [],
        "etapas": [
            {"id_etapa": "1", "descricao": "Primeiro Contato"},
            {"id_etapa": "2", "descricao": "Análise de Necessidades"},
            {"id_etapa": "3", "descricao": "Proposta Enviada"},
            {"id_etapa": "4", "descricao": "Fechamento"}
        ],
        "propostas": []
    }

def save_database(data):
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Funções auxiliares
def format_date(date_str):
    if date_str and "T" in date_str:
        return date_str.split("T")[0]
    return date_str

def get_consultores(db):
    return [c["id_consultores"] for c in db["consultores"] if c.get("id_consultores")]

def get_propostas(db):
    return [p["idNumPropostas"] for p in db["propostas"] if p.get("idNumPropostas")]

def get_etapas(db):
    return [(e["id_etapa"], e["descricao"]) for e in db["etapas"] if e.get("id_etapa")]

# Interface Streamlit
def main():
    st.title("📋 Sistema de Gerenciamento de Atendimentos")
    
    # Menu lateral
    menu_option = st.sidebar.selectbox(
        "Menu Principal",
        ["Cadastrar Atendimento", "Listar Atendimentos", "Editar Atendimento", 
         "Gerenciar Propostas", "Gerenciar Consultores", "Gerenciar Etapas", "Exportar Dados"]
    )
    
    db = load_database()
    
    if menu_option == "Cadastrar Atendimento":
        st.header("Novo Atendimento")
        with st.form("form_atendimento"):
            col1, col2 = st.columns(2)
            
            with col1:
                idChecagem = st.selectbox("Status", ["Não Lançado", "Lançado"])
                
                # Combobox para Propostas
                propostas_disponiveis = get_propostas(db)
                idNumPropostas = st.selectbox(
                    "Nº Proposta",
                    options=propostas_disponiveis,
                    index=0 if propostas_disponiveis else None,
                    format_func=lambda x: f"Proposta: {x}" if x else "Nenhuma proposta cadastrada"
                )
                
                idRazaoSocial = st.text_input("Razão Social")
                
                # Combobox para Etapas
                etapas_disponiveis = get_etapas(db)
                idEtapa = st.selectbox(
                    "Etapa",
                    options=etapas_disponiveis,
                    format_func=lambda x: f"{x[0]} - {x[1]}",
                    index=0 if etapas_disponiveis else None
                )
                
                idObservacao = st.text_area("Observações")
                
            with col2:
                idHoraVisita = st.text_input("Hora Visita")
                idDataVisita = st.date_input("Data Visita", datetime.now())
                
                # Combobox para Consultores
                consultores_disponiveis = get_consultores(db)
                idConsultor = st.selectbox(
                    "Consultor",
                    options=consultores_disponiveis,
                    index=0 if consultores_disponiveis else None,
                    format_func=lambda x: x if x else "Nenhum consultor cadastrado"
                )
                
                idAtendNIF = st.text_input("NIF Atendimento")
                idCNPJ = st.text_input("CNPJ")
                idProduto = st.text_input("Produto")
                idHoraAtend = st.text_input("Hora Atendimento")
                idData = st.date_input("Data Atendimento", datetime.now())
            
            if st.form_submit_button("Salvar Atendimento"):
                novo_atendimento = {
                    "idChecagem": idChecagem,
                    "idNumPropostas": idNumPropostas,
                    "idRazaoSocial": idRazaoSocial,
                    "idEtapa": idEtapa[0] if idEtapa else None,
                    "idObservacao": idObservacao if idObservacao else None,
                    "idHoraVisita": idHoraVisita,
                    "idDataVisita": str(idDataVisita),
                    "idConsultor": idConsultor,
                    "idAtendNIF": idAtendNIF,
                    "idCNPJ": idCNPJ,
                    "idProduto": idProduto,
                    "idHoraAtend": idHoraAtend if idHoraAtend else None,
                    "idData": str(idData),
                    "detalhesProposta": None,
                    "detalhesConsultor": None
                }
                
                # Buscar detalhes da proposta selecionada
                if idNumPropostas:
                    for proposta in db["propostas"]:
                        if proposta["idNumPropostas"] == idNumPropostas:
                            novo_atendimento["detalhesProposta"] = proposta
                            break
                
                # Buscar detalhes do consultor selecionado
                if idConsultor:
                    for consultor in db["consultores"]:
                        if consultor["id_consultores"] == idConsultor:
                            novo_atendimento["detalhesConsultor"] = consultor
                            break
                
                db["atendimentos"].append(novo_atendimento)
                save_database(db)
                st.success("Atendimento cadastrado com sucesso!")
                st.balloons()
    
    elif menu_option == "Listar Atendimentos":
        st.header("Lista de Atendimentos")
        
        # Filtros
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
        with col_filtro1:
            filtro_status = st.selectbox("Filtrar por Status", ["Todos", "Lançado", "Não Lançado"])
        with col_filtro2:
            filtro_consultor = st.selectbox(
                "Filtrar por Consultor",
                ["Todos"] + get_consultores(db)
            )
        with col_filtro3:
            filtro_etapa = st.selectbox(
                "Filtrar por Etapa",
                ["Todos"] + [f"{e[0]} - {e[1]}" for e in get_etapas(db)]
            )
        
        # Tabela de atendimentos
        dados_tabela = []
        for atendimento in db["atendimentos"]:
            # Aplicar filtros
            status_ok = (filtro_status == "Todos" or atendimento["idChecagem"] == filtro_status)
            consultor_ok = (filtro_consultor == "Todos" or atendimento.get("idConsultor") == filtro_consultor)
            
            # Obter descrição da etapa para filtro
            etapa_desc = ""
            for etapa in db["etapas"]:
                if etapa["id_etapa"] == atendimento.get("idEtapa"):
                    etapa_desc = f"{etapa['id_etapa']} - {etapa['descricao']}"
                    break
            
            etapa_ok = (filtro_etapa == "Todos" or etapa_desc == filtro_etapa)
            
            if status_ok and consultor_ok and etapa_ok:
                dados_tabela.append([
                    atendimento["idNumPropostas"],
                    atendimento["idRazaoSocial"],
                    atendimento["idCNPJ"],
                    atendimento["idConsultor"],
                    atendimento["idChecagem"],
                    format_date(atendimento["idData"]),
                    etapa_desc
                ])
        
        if dados_tabela:
            st.dataframe(
                dados_tabela,
                column_config={
                    0: "Proposta",
                    1: "Razão Social",
                    2: "CNPJ",
                    3: "Consultor",
                    4: "Status",
                    5: "Data",
                    6: "Etapa"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("Nenhum atendimento encontrado com os filtros selecionados.")
    
    elif menu_option == "Editar Atendimento":
        st.header("Editar Atendimento")
        
        if not db["atendimentos"]:
            st.warning("Nenhum atendimento cadastrado para editar.")
        else:
            atendimentos_select = [f"{at['idNumPropostas']} - {at['idRazaoSocial']}" for at in db["atendimentos"]]
            atendimento_selecionado = st.selectbox("Selecione o atendimento", atendimentos_select)
            
            index_atendimento = atendimentos_select.index(atendimento_selecionado)
            atendimento = db["atendimentos"][index_atendimento]
            
            with st.form("form_editar_atendimento"):
                col1, col2 = st.columns(2)
                
                with col1:
                    novo_idChecagem = st.selectbox(
                        "Status", 
                        ["Não Lançado", "Lançado"],
                        index=0 if atendimento["idChecagem"] == "Não Lançado" else 1
                    )
                    
                    # Combobox para Propostas
                    propostas_disponiveis = get_propostas(db)
                    novo_idNumPropostas = st.selectbox(
                        "Nº Proposta",
                        options=propostas_disponiveis,
                        index=propostas_disponiveis.index(atendimento["idNumPropostas"]) if atendimento["idNumPropostas"] in propostas_disponiveis else 0
                    )
                    
                    novo_idRazaoSocial = st.text_input("Razão Social", value=atendimento["idRazaoSocial"])
                    
                    # Combobox para Etapas
                    etapas_disponiveis = get_etapas(db)
                    etapa_atual = next((e for e in etapas_disponiveis if e[0] == atendimento["idEtapa"]), None)
                    novo_idEtapa = st.selectbox(
                        "Etapa",
                        options=etapas_disponiveis,
                        format_func=lambda x: f"{x[0]} - {x[1]}",
                        index=etapas_disponiveis.index(etapa_atual) if etapa_atual in etapas_disponiveis else 0
                    )
                    
                    novo_idObservacao = st.text_area(
                        "Observações", 
                        value=atendimento["idObservacao"] if atendimento["idObservacao"] else ""
                    )
                    
                with col2:
                    novo_idHoraVisita = st.text_input("Hora Visita", value=atendimento["idHoraVisita"])
                    novo_idDataVisita = st.date_input(
                        "Data Visita", 
                        value=datetime.strptime(atendimento["idDataVisita"], "%Y-%m-%d") if atendimento["idDataVisita"] else datetime.now()
                    )
                    
                    # Combobox para Consultores
                    consultores_disponiveis = get_consultores(db)
                    novo_idConsultor = st.selectbox(
                        "Consultor",
                        options=consultores_disponiveis,
                        index=consultores_disponiveis.index(atendimento["idConsultor"]) if atendimento["idConsultor"] in consultores_disponiveis else 0
                    )
                    
                    novo_idAtendNIF = st.text_input("NIF Atendimento", value=atendimento["idAtendNIF"])
                    novo_idCNPJ = st.text_input("CNPJ", value=atendimento["idCNPJ"])
                    novo_idProduto = st.text_input("Produto", value=atendimento["idProduto"])
                    novo_idHoraAtend = st.text_input(
                        "Hora Atendimento", 
                        value=atendimento["idHoraAtend"] if atendimento["idHoraAtend"] else ""
                    )
                    novo_idData = st.date_input(
                        "Data Atendimento", 
                        value=datetime.strptime(atendimento["idData"], "%Y-%m-%d") if atendimento["idData"] else datetime.now()
                    )
                
                if st.form_submit_button("Atualizar Atendimento"):
                    atendimento_atualizado = {
                        "idChecagem": novo_idChecagem,
                        "idNumPropostas": novo_idNumPropostas,
                        "idRazaoSocial": novo_idRazaoSocial,
                        "idEtapa": novo_idEtapa[0] if novo_idEtapa else None,
                        "idObservacao": novo_idObservacao if novo_idObservacao else None,
                        "idHoraVisita": novo_idHoraVisita,
                        "idDataVisita": str(novo_idDataVisita),
                        "idConsultor": novo_idConsultor,
                        "idAtendNIF": novo_idAtendNIF,
                        "idCNPJ": novo_idCNPJ,
                        "idProduto": novo_idProduto,
                        "idHoraAtend": novo_idHoraAtend if novo_idHoraAtend else None,
                        "idData": str(novo_idData),
                        "detalhesProposta": None,
                        "detalhesConsultor": None
                    }
                    
                    # Atualizar relacionamentos
                    if novo_idNumPropostas:
                        for proposta in db["propostas"]:
                            if proposta["idNumPropostas"] == novo_idNumPropostas:
                                atendimento_atualizado["detalhesProposta"] = proposta
                                break
                    
                    if novo_idConsultor:
                        for consultor in db["consultores"]:
                            if consultor["id_consultores"] == novo_idConsultor:
                                atendimento_atualizado["detalhesConsultor"] = consultor
                                break
                    
                    db["atendimentos"][index_atendimento] = atendimento_atualizado
                    save_database(db)
                    st.success("Atendimento atualizado com sucesso!")
                    st.rerun()
    
    elif menu_option == "Gerenciar Propostas":
        st.header("Propostas Comerciais")
        
        tab1, tab2 = st.tabs(["Listar Propostas", "Nova Proposta"])
        
        with tab1:
            if db["propostas"]:
                dados_tabela = []
                for proposta in db["propostas"]:
                    dados_tabela.append([
                        proposta["idNumPropostas"],
                        proposta["idRazaoSocial"],
                        proposta["idCNPJ"],
                        proposta["idProduto"],
                        proposta["idHorasContratadas"],
                        format_date(proposta["idData"])
                    ])
                
                st.dataframe(
                    dados_tabela,
                    column_config={
                        0: "Nº Proposta",
                        1: "Razão Social",
                        2: "CNPJ",
                        3: "Produto",
                        4: "Horas Contratadas",
                        5: "Data"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("Nenhuma proposta cadastrada.")
        
        with tab2:
            with st.form("form_proposta"):
                col1, col2 = st.columns(2)
                
                with col1:
                    idNumPropostas = st.text_input("Número da Proposta*")
                    idRazaoSocial = st.text_input("Razão Social*")
                    idCNPJ = st.text_input("CNPJ*")
                    
                with col2:
                    idProduto = st.text_input("Produto*")
                    idHorasContratadas = st.number_input("Horas Contratadas", min_value=0)
                    idData = st.date_input("Data da Proposta", datetime.now())
                
                if st.form_submit_button("Salvar Proposta"):
                    if not idNumPropostas or not idRazaoSocial or not idCNPJ or not idProduto:
                        st.error("Campos marcados com * são obrigatórios!")
                    else:
                        nova_proposta = {
                            "idNumPropostas": idNumPropostas,
                            "idRazaoSocial": idRazaoSocial,
                            "idCNPJ": idCNPJ,
                            "idProduto": idProduto,
                            "idHorasContratadas": idHorasContratadas,
                            "idData": str(idData)
                        }
                        
                        # Atualizar atendimentos relacionados
                        for atendimento in db["atendimentos"]:
                            if atendimento["idNumPropostas"] == idNumPropostas:
                                atendimento["detalhesProposta"] = nova_proposta
                        
                        db["propostas"].append(nova_proposta)
                        save_database(db)
                        st.success("Proposta cadastrada com sucesso!")
                        st.balloons()
    
    elif menu_option == "Gerenciar Consultores":
        st.header("Consultores")
        
        tab1, tab2 = st.tabs(["Listar Consultores", "Novo Consultor"])
        
        with tab1:
            if db["consultores"]:
                st.dataframe(
                    db["consultores"],
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("Nenhum consultor cadastrado.")
        
        with tab2:
            with st.form("form_consultor"):
                id_consultores = st.text_input("Nome do Consultor*")
                id_NIF = st.text_input("NIF do Consultor")
                
                if st.form_submit_button("Salvar Consultor"):
                    if not id_consultores:
                        st.error("O nome do consultor é obrigatório!")
                    else:
                        novo_consultor = {
                            "id_consultores": id_consultores,
                            "id_NIF": id_NIF if id_NIF else None
                        }
                        
                        # Atualizar atendimentos relacionados
                        for atendimento in db["atendimentos"]:
                            if atendimento["idConsultor"] == id_consultores:
                                atendimento["detalhesConsultor"] = novo_consultor
                        
                        db["consultores"].append(novo_consultor)
                        save_database(db)
                        st.success("Consultor cadastrado com sucesso!")
                        st.balloons()
    
    elif menu_option == "Gerenciar Etapas":
        st.header("Gestão de Etapas")
        
        tab1, tab2 = st.tabs(["Listar Etapas", "Nova Etapa"])
        
        with tab1:
            if db["etapas"]:
                st.dataframe(
                    db["etapas"],
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "id_etapa": "Código",
                        "descricao": "Descrição"
                    }
                )
            else:
                st.info("Nenhuma etapa cadastrada.")
        
        with tab2:
            with st.form("form_etapa"):
                col1, col2 = st.columns(2)
                
                with col1:
                    id_etapa = st.text_input("Código da Etapa* (Ex: 1, 2, 3...)")
                with col2:
                    descricao = st.text_input("Descrição da Etapa*")
                
                if st.form_submit_button("Salvar Etapa"):
                    if not id_etapa or not descricao:
                        st.error("Todos os campos são obrigatórios!")
                    elif any(e["id_etapa"] == id_etapa for e in db["etapas"]):
                        st.error("Já existe uma etapa com este código!")
                    else:
                        nova_etapa = {
                            "id_etapa": id_etapa,
                            "descricao": descricao
                        }
                        
                        db["etapas"].append(nova_etapa)
                        save_database(db)
                        st.success("Etapa cadastrada com sucesso!")
                        st.balloons()
    
    elif menu_option == "Exportar Dados":
        st.header("Exportação de Dados")
        
        st.download_button(
            label="Baixar Banco de Dados Completo",
            data=json.dumps(db, ensure_ascii=False, indent=4),
            file_name="database_export.json",
            mime="application/json"
        )
        
        st.divider()
        st.subheader("Estatísticas")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Atendimentos", len(db["atendimentos"]))
        col2.metric("Total Propostas", len(db["propostas"]))
        col3.metric("Total Consultores", len(db["consultores"]))
        col4.metric("Total Etapas", len(db["etapas"]))

if __name__ == "__main__":
    main()
