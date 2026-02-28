You’re almost set! To be able to activate your Private Email subscription to receive mail and create mailboxes, you must first set up these important DNS records from the table below. You can find a little help to do this in our handy step-by-step guide. Once completed, please allow up to 4 hours for the changes to take effect.

Hostname	Record type	Priority	Value
@	MX	10	mx1.privateemail.com
@	MX	10	mx2.privateemail.com
@	TXT		



---------------------------------------------------------------------------------------------------------------------------------------------------------

Electric vehicles are a key enabler for reducing greenhouse gas emissions and are progressively transforming contemporary transportation systems.
Limited driving range, sparse charging infrastructure, and long charging durations remain major barriers to large-scale transportation electrification. 


DWC, a cornerstone of the broader electrified road system (ERS) paradigm, represents a transformative approach to achieving carbon-neutral transport by facilitating energy replenishment while vehicles are in motion. 

This process typically employs near-field inductive coupling to facilitate the contactless transfer of energy from grid-connected transmitters embedded in the roadway to pick-up receivers mounted beneath the vehicle. This seamless integration of energy delivery and transportation supports the continuous operation of vehicle fleets, which is essential for maximizing service efficiency in transportation and high-frequency logistics.

From a design perspective, the ability to replenish energy en-route allows for significant reductions in onboard battery capacity, reducing vehicle weight and alleviating the common technical trade-off between driving range and manufacturing costs. 

Furthermore, the deployment of WCL infrastructure utilizes existing road footprints without requiring additional urban land, making it a highly attractive solution for high-density cities with limited space. 

Ultimately, the strategic deployment of dynamic charging infrastructure aims to alleviate range anxiety and foster a more resilient, sustainable mobility ecosystem by allowing vehicles to operate with reduced battery capacities while achieving extended driving ranges.


While ERS enables continuous fleet operation and mitigates range anxiety by allowing for a significant reduction in onboard battery capacity, the technology still faces substantial hurdles, including high initial capital expenditures for roadside infrastructure deployment and complex institutional requirements for cross-border technical coordination. 

Moreover, equipping all road segments with DWC facilities remains economically infeasible given current deployment costs. 

It is also important to note that dynamic charging systems exhibit lower energy transfer efficiency compared to conventional stationary charging; consequently, DWC is intended to extend the operational driving range of electric vehicles rather than to supplant the need for static charging infrastructure. 

This interplay between discrete and continuous charging opportunities introduces new complexities into the vehicle routing problem, necessitating integrated optimization frameworks that can jointly reason over both infrastructure types to minimize travel time.


---------------------------------------------------------------------------------------------------------------------------------------------------------


Intelligent Transportation Systems (ITS) are now the digital backbone of modern transport networks, providing the real-time sensing, communication, and control needed to keep cities moving safely and sustainably. 

By fusing roadside sensors, connected vehicles, and data analytics, ITS applications, adaptive signal control, incident-response guidance, and multimodal coordination consistently cut crashes, ease congestion, and lower urban emissions while underpinning wider smart-city services. 

Electric vehicles (EVs) fit naturally into this ecosystem: their native Vehicle-to-Everything (V2X) connectivity allows them to broadcast state-of-charge and position, so ITS platforms can schedule eco-routes, book battery-segment swaps, and balance grid demand in real time~\cite{chen2023development}.

\vspace{1em}
% EV, environment, Charging, issues with charging
In pursuit of climate change mitigation, governments worldwide are accelerating the transition to EVs in transport fleets~\cite{wang2021taxi}. For example, China has set targets to peak carbon emissions by 2030 and achieve carbon neutrality by 2060~\cite{liu2023optimizing}, and countries like the Netherlands have mandated all new passenger vehicles to be zero-emission by 2030~\cite{rvo2020electric}. Similarly, Canada is committed to achieving net-zero emissions by 2050~\cite{canada_2030erp}. To support this ambitious goal, the nation is rolling out a comprehensive plan for the transportation sector. A key component of this strategy is the development of a Light-Duty Vehicle (LDV) Zero Emission Vehicle (ZEV) sales mandate. This mandate will feature annually increasing requirements, culminating in 100\% ZEV sales by 2035. This policy push has spurred the adoption of EVs in urban logistics as a means to reduce greenhouse gas and air pollutant emissions in cities. EVs offer benefits such as zero tailpipe emissions and lower noise, aligning with sustainable urban freight goals. However, the electrification of urban delivery fleets also presents significant challenges. Unlike internal combustion engine vehicles (ICEVs) that can be refueled in minutes, EVs require specialized charging infrastructure and considerable charging time, even fast chargers typically need on the order of 20-60 minutes to restore 80\% of battery capacity~\cite{dot2025charging_speeds}. This limited driving range and lengthy recharge process can disrupt logistics operations, forcing delivery vehicles to spend valuable time off-route to charge. Fleet operators thus face range anxiety and operational constraints in scheduling deliveries, as insufficient charging opportunities or long charging or lost productivity. These issues highlight the need for innovative strategies to manage energy and routing in electric urban logistics.

\vspace{1em}
% BSS, solution of range axity
Battery swapping has emerged as a promising solution to mitigate EV charging delays and ensure high vehicle utilization. In a battery swapping system, a depleted EV battery can be quickly exchanged for a fully charged battery at a swapping station, instead of waiting for the vehicle to charge conventionally. This approach decouples energy replenishment from the vehicle and dramatically reduces waiting times. Compared to plug-in charging, battery swapping can accomplish energy replenishment in a time comparable to refueling a conventional vehicle. Swap operations for standardized battery packs have been demonstrated to take as little as one or two minutes~\cite{mak2013infrastructure}, effectively minimizing vehicle downtime. The high accessibility and fast turnaround of battery swapping stations (BSSs) make them attractive for commercial fleet use, as vehicles can resume their routes almost immediately after a swap. Moreover, swapping offers additional benefits in terms of energy management and sustainability. Swapping enables batteries to be centrally recharged at off-peak hours, which can reduce peak load stress on the electrical grid and allow increased use of renewable energy~\cite{han2023routing}. It also facilitates battery recycling and lifecycle management by centralizing used batteries at swap stations. Studies indicate that a swapping regime can better support battery health monitoring, second-life applications, and end-of-life recycling than decentralized charging~\cite{ma2024pathway}. The process of swapping a few smaller, lighter modules can be significantly faster than replacing a single, heavy battery pack. This reduction in swapping time minimizes vehicle downtime and increases the overall productivity of the fleet. The long-term operational costs can also be substantially reduced through the adoption of modular batteries. In a traditional electric vehicle, the failure of a single battery cell often necessitates the replacement of the entire expensive battery pack. With a modular system, a faulty module can be individually identified and replaced, which is a much quicker and more cost-effective repair. Switching to modular battery blocks allows electric taxi drivers to choose the amount of battery they need, making battery swapping stations more profitable and flexible. Plus, it can cut the upfront cost of buying batteries by 38\%~\cite{liu2023optimizing}.


---------------------------------------------------------------------------------------------------------------------------------------------------------



