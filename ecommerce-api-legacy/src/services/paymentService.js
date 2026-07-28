/**
 * Simulação de processamento de pagamento (nenhum gateway real integrado —
 * fora do escopo deste desafio). A validação de formato do cartão usa o
 * algoritmo de Luhn, em vez da regra antiga de aprovar qualquer número
 * que comece com "4".
 */
function luhnCheck(cardNumber) {
    const digits = String(cardNumber).replace(/\D/g, '');
    if (digits.length < 13) return false;

    let sum = 0;
    let shouldDouble = false;
    for (let i = digits.length - 1; i >= 0; i--) {
        let digit = parseInt(digits[i], 10);
        if (shouldDouble) {
            digit *= 2;
            if (digit > 9) digit -= 9;
        }
        sum += digit;
        shouldDouble = !shouldDouble;
    }
    return sum % 10 === 0;
}

function processarPagamento(numeroCartao) {
    const aprovado = luhnCheck(numeroCartao);
    return aprovado ? 'PAID' : 'DENIED';
}

module.exports = { luhnCheck, processarPagamento };
