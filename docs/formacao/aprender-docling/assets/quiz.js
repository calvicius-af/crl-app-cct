/* Componente de quiz partilhado pelas lições "Aprender Docling".
 *
 * Serve a prática de recuperação (retrieval practice): o feedback é imediato e
 * automático, e a resposta errada explica-se em vez de se limitar a corrigir.
 *
 * Marcação esperada:
 *
 *   <div class="quiz" data-certa="1">
 *     <p class="pergunta">…</p>
 *     <div class="opcoes">
 *       <button>…</button>
 *       <button>…</button>
 *     </div>
 *     <p class="feedback" data-certa="…" data-errada="…"></p>
 *   </div>
 *
 * `data-certa` no contentor é o índice (base 0) da opção correcta.
 */
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".quiz").forEach(function (quiz) {
    var certa = parseInt(quiz.dataset.certa, 10);
    var botoes = Array.prototype.slice.call(quiz.querySelectorAll(".opcoes button"));
    var feedback = quiz.querySelector(".feedback");

    botoes.forEach(function (botao, i) {
      botao.addEventListener("click", function () {
        var acertou = i === certa;
        botoes.forEach(function (b, j) {
          b.disabled = true;
          if (j === certa) b.classList.add("certa");
        });
        if (!acertou) botao.classList.add("errada");
        if (feedback) {
          feedback.textContent = acertou
            ? feedback.dataset.certa
            : feedback.dataset.errada;
          feedback.classList.add("visivel");
        }
      });
    });
  });
});
