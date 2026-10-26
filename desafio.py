
from abc import ABC, abstractmethod
from datetime import datetime


class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append(transacao)


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @classmethod
    def nova_conta(cls, cliente, numero):
        return ContaCorrente(numero, cliente)

    def sacar(self, valor):
        if valor <= 0:
            print("Valor inválido.")
            return False

        if valor > self._saldo:
            print("Saldo insuficiente.")
            return False

        self._saldo -= valor
        print("Saque realizado com sucesso!")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("Valor inválido.")
            return False

        self._saldo += valor
        print("Depósito realizado com sucesso!")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500.0, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        historico = self.historico.transacoes
        saques_realizados = sum(
            1 for transacao in historico
            if transacao["tipo"] == "Saque"
        )

        if valor <= 0:
            print("Valor inválido.")
            return False

        if valor > self._limite:
            print("O valor máximo por saque é R$ 500,00.")
            return False

        if saques_realizados >= self._limite_saques:
            print("Limite de saques diários atingido.")
            return False

        return super().sacar(valor)


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento


class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao({
                "tipo": "Depósito",
                "valor": self.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })


class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao({
                "tipo": "Saque",
                "valor": self.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })


def ler_valor(mensagem):
    try:
        return float(input(mensagem).replace(",", "."))
    except ValueError:
        print("Entrada inválida! Digite um número.")
        return None


def encontrar_cliente(clientes, cpf):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None


def cadastrar_cliente(clientes):
    cpf = input("Informe o CPF (somente números): ").strip()

    if not cpf.isdigit() or len(cpf) != 11:
        print("CPF inválido. Digite os 11 números.")
        return

    if encontrar_cliente(clientes, cpf):
        print("Já existe um cliente com esse CPF.")
        return

    nome = input("Nome completo: ").strip()
    data_texto = input("Data de nascimento (DD/MM/AAAA): ").strip()
    endereco = input(
        "Endereço (logradouro, número - bairro - cidade/UF): "
    ).strip()

    if not nome or not data_texto or not endereco:
        print("Todos os campos são obrigatórios.")
        return

    try:
        data_nascimento = datetime.strptime(
            data_texto, "%d/%m/%Y"
        ).date()
    except ValueError:
        print("Data inválida. Use o formato DD/MM/AAAA.")
        return

    cliente = PessoaFisica(
        cpf=cpf,
        nome=nome,
        data_nascimento=data_nascimento,
        endereco=endereco
    )

    clientes.append(cliente)
    print("Cliente cadastrado com sucesso!")


def criar_conta(clientes, contas, numero_conta):
    cpf = input("Informe o CPF do titular: ").strip()
    cliente = encontrar_cliente(clientes, cpf)

    if cliente is None:
        print("Cliente não encontrado. Cadastre-o primeiro.")
        return numero_conta

    conta = Conta.nova_conta(cliente, numero_conta)
    cliente.adicionar_conta(conta)
    contas.append(conta)

    print("Conta corrente criada com sucesso!")
    print(f"Agência: {conta.agencia}")
    print(f"Número da conta: {conta.numero}")
    print(f"Titular: {cliente.nome}")

    return numero_conta + 1


def selecionar_conta(contas):
    if not contas:
        print("Nenhuma conta cadastrada.")
        return None

    cpf = input("Informe o CPF do titular: ").strip()

    encontradas = [
        conta for conta in contas
        if conta.cliente.cpf == cpf
    ]

    if not encontradas:
        print("Nenhuma conta encontrada para esse CPF.")
        return None

    if len(encontradas) == 1:
        return encontradas[0]

    print("\nContas encontradas:")
    for conta in encontradas:
        print(f"Conta: {conta.numero}")

    try:
        numero = int(input("Digite o número da conta: "))
    except ValueError:
        print("Número inválido.")
        return None

    for conta in encontradas:
        if conta.numero == numero:
            return conta

    print("Conta não encontrada.")
    return None


def exibir_extrato(conta):
    print("\n===== EXTRATO =====")

    transacoes = conta.historico.transacoes

    if not transacoes:
        print("Nenhuma movimentação realizada.")
    else:
        for transacao in transacoes:
            print(
                f"{transacao['data']} - {transacao['tipo']}: "
                f"R$ {transacao['valor']:.2f}"
            )

    print(f"Saldo atual: R$ {conta.saldo:.2f}")


def main():
    clientes = []
    contas = []
    numero_conta = 1

    while True:
        print("\n===== SISTEMA BANCÁRIO =====")
        print("[1] Cadastrar cliente")
        print("[2] Criar conta corrente")
        print("[3] Depositar")
        print("[4] Sacar")
        print("[5] Extrato")
        print("[0] Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_cliente(clientes)

        elif opcao == "2":
            numero_conta = criar_conta(
                clientes, contas, numero_conta
            )

        elif opcao in ("3", "4", "5"):
            conta = selecionar_conta(contas)

            if conta is None:
                continue

            if opcao == "3":
                valor = ler_valor("Valor do depósito: R$ ")
                if valor is not None:
                    cliente = conta.cliente
                    cliente.realizar_transacao(
                        conta, Deposito(valor)
                    )

            elif opcao == "4":
                valor = ler_valor("Valor do saque: R$ ")
                if valor is not None:
                    cliente = conta.cliente
                    cliente.realizar_transacao(
                        conta, Saque(valor)
                    )

            elif opcao == "5":
                exibir_extrato(conta)

        elif opcao == "0":
            print("Obrigado por utilizar nosso sistema!")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
