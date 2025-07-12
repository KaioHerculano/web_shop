# Web Shop - Supermercado Online 🛒🥦

Bem-vindo ao repositório oficial do **Web Shop**, um site de supermercado online desenvolvido com Django e Bootstrap. A plataforma permite que usuários explorem categorias de produtos, adicionem itens ao carrinho e realizem pedidos de forma prática e rápida.

## 💡 Sobre o Projeto

O **Web Shop** tem como objetivo oferecer uma solução completa para compras online de supermercado, com uma interface simples, moderna e acessível. O projeto foi desenvolvido como parte de um estudo acadêmico de sistemas web com foco em usabilidade, performance e experiência do usuário.

### 🔗 Integração com o Sales_Hub

Este sistema é **totalmente integrado com o [Sales_Hub]**, um sistema de **gestão de estoque** também desenvolvido com Django. Através dessa integração, os produtos exibidos no Web Shop são sincronizados com o estoque gerenciado no Sales_Hub, garantindo consistência, controle de vendas e atualização automática de quantidades disponíveis.

## 🛠 Tecnologias Utilizadas

- **Python 3.11**
- **Django 4.x**
- **Bootstrap 5**
- **HTML5 e CSS3**
- **SQLite** (desenvolvimento)
- **Docker** (desenvolvimento)

## 🔑 Principais Funcionalidades

- Página inicial com destaques e promoções
- Filtro de produtos por categoria
- Carrinho de compras com total dinâmico
- Envio de pedidos via WhatsApp
- Autenticação de usuários responsáveis pelo site
- Layout responsivo para desktop e mobile
- Painel administrativo para gerenciar produtos e pedidos

## 🚀 Como Executar Localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate no Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Realize as migrações e execute o servidor:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. Acesse: `http://127.0.0.1:8000`

## 📷 Capturas de Tela

### Topo da página
![Página Inicial](screenshot/topo.png)

### Lista de Categorias
![Lista de Produtos](screenshot/categorias.png)

### Produtos
![Rodapé](screenshot/produtos.png)

### Ofertas
![Rodapé](screenshot/ofertas.png)

### Carrinho de Compras
![Rodapé](screenshot/carrinho.png)

### Finalizar Pedido
![Rodapé](screenshot/finalizar_pedido.png)

### Sobre
![Carrinho](screenshot/sobre.png)

### Rodapé
![Rodapé](screenshot/footer.png)

## 🙋 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.
