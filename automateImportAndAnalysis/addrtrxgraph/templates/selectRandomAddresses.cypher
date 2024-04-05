// Se ci sono dei nodi con label Sampled da un chunk precedente importato allora rimuovi la label per tutti i nodi che la hanno 
MATCH (a:Sampled)
REMOVE a:Sampled;

// Considera i nuovi nodi che sono coinvolti come input in transazioni ed etichettali, quelli precedenti (se è stato importato almeno un chunk) sono già stati etichettati
CALL apoc.periodic.iterate(
    "MATCH (a:Address)-[:INPUT]->(:Transaction)
     WHERE NOT a:Input // evito di considerare nodi già considerati in passato ma solo quelli del nuovo chunk importato
	 RETURN a",
    "SET a:Input",
    {batchSize: 10000}
);

// Fino a quando non abbiamo etichettato con label Sampled n = 1000 nodi scegli casualmente dei nodi Input (cioè indirizzi che sono stati coinvolti come input in almeno una transazione) tra tutti quelli presenti nel database e etichettali come :Sampled
CALL {
  MATCH (i:Input)
  WITH count(i) AS num_input
  CALL apoc.periodic.commit(
    "MATCH (i:Input) 
    WITH i
    SKIP toInteger(floor($num_input*rand())) 
    LIMIT 1 
    SET i:Sampled 
    WITH 1 AS dummy 
    MATCH (n:Sampled) 
    RETURN 1000 - count(n)",
  {num_input: num_input})
  YIELD updates, executions
  RETURN updates, executions
}

// Salva su file i nodi Sampled
CALL apoc.export.csv.query(
  "MATCH (a:Sampled)
   WITH collect(a.addressId) as randomAddresses
   UNWIND randomAddresses AS randomAddress
   RETURN randomAddress",
  "randomAddresses_chunk_x.txt",
{quotes: "none"}
) YIELD file
RETURN "Generazione indirizzi completata su file "