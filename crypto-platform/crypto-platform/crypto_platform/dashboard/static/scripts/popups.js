//Form Popups
function openDepositForm() {
    document.getElementById("depositForm").style.display = "block";
}

function closeDepositForm() {
    document.getElementById("depositForm").style.display = "none";
}

function openBuyBasketForm() {
    document.getElementById("buyBasketForm").style.display = "block";
}

function closeBuyBasketForm() {
    document.getElementById("buyBasketForm").style.display = "none";
}

function openSellBasketForm() {
    document.getElementById("sellBasketForm").style.display = "block";
}

function closeSellBasketForm() {
    document.getElementById("sellBasketForm").style.display = "none";
}

function openWithdrawForm() {
    document.getElementById("withdrawForm").style.display = "block";
}

function closeWithdrawForm() {
    document.getElementById("withdrawForm").style.display = "none";
}

function openTaxLossHarvestForm() {
    document.getElementById("taxLossHarvestForm").style.display = "block";
}

function closeTaxLossHarvestForm() {
    document.getElementById("taxLossHarvestForm").style.display = "none";
}

function openRetryBuysForm() {
    document.getElementById("retryBuysForm").style.display = "block";
}

function closeRetryBuysForm() {
    document.getElementById("retryBuysForm").style.display = "none";
}

function openRetrySellsForm() {
    document.getElementById("retrySellsForm").style.display = "block";
}

function closeRetrySellsForm() {
    document.getElementById("retrySellsForm").style.display = "none";
}

//Other Popups
function closeSuccessPopup() {
    document.getElementById("successPopup").style.display = "none";
}

function closeErrorPopup() {
    document.getElementById("errorPopup").style.display = "none";
}

function closeFailedBuyErrorPopup() {
    document.getElementById("failedbuyerrorPopup").style.display = "none";
}

function closeFailedSellErrorPopup() {
    document.getElementById("failedsellerrorPopup").style.display = "none";
}

//Open web forms on page load
function openWebForms() {
    if ("{{ showTaxLossHarvestForm }}" == "True") {
        openTaxLossHarvestForm();
    }
}