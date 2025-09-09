### Health Score Methodology

The **Health Score** measures overall customer engagement and satisfaction as a weighted sum of key behaviors:

<pre class="overflow-visible!" data-start="206" data-end="430"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>health_score = (login_score × w_login) +
               (feature_score × w_feature) +
               (ticket_score × w_ticket) +
               (invoice_payment_score × w_invoice) +
               (api_score × w_api)
</span></span></code></div></div></pre>

* **Weights (`w_*`)** reflect the relative importance of each behavior. For example, frequent logins and feature adoption may carry more weight than API usage if platform engagement is the main goal.
* Each sub-score represents a specific activity: logins, feature usage, support tickets, invoice payments, and API usage.
* The resulting score helps identify highly engaged customers versus those at risk, guiding customer success strategies.

**Thinking of Weights:**

Weights should reflect business priorities. For instance:

* **Login and feature usage:** core engagement → higher weight
* **Ticket score:** fewer issues → moderate weight
* **Invoice payments:** financial health → moderate weight
* **API usage:** optional integration → lower weight
