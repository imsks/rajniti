from bs4 import BeautifulSoup

html_content = """<div class="box-wraper box-boarder">
    <div class="container-fluid">
        <div class="row">

                        <div class="col-md-4 col-12">
                <div class="cand-box">
                    <figure><img src="https://results.eci.gov.in/uploads1/candprofile/E27/2024/AC/S13/RAJES-2024-20241104033836.jpg" alt=""></figure>
                    <div class="cand-info">
                        <div class="status won">
                            <div style="text-transform: capitalize">won</div>
                            <div>146839 <span>(+ 53204)</span></div>
                        </div>
                        <div class="nme-prty">
                            <h5>RAJESH UDESING PADVI</h5>
                            <h6>Bharatiya Janata Party</h6>
                        </div>
                    </div>
                </div>
            </div>
                        <div class="col-md-4 col-12">
                <div class="cand-box">
                    <figure><img src="https://results.eci.gov.in/uploads1/candprofile/E27/2024/AC/S13/RAJED-2024-20241104033933.jpg" alt=""></figure>
                    <div class="cand-info">
                        <div class="status lost">
                            <div style="text-transform: capitalize">lost</div>
                            <div>93635 <span>( -53204)</span></div>
                        </div>
                        <div class="nme-prty">
                            <h5>RAJENDRAKUMAR KRISHNARAO GAVIT</h5>
                            <h6>Indian National Congress</h6>
                        </div>
                    </div>
                </div>
            </div>
                        <div class="col-md-4 col-12">
                <div class="cand-box">
                    <figure><img src="https://results.eci.gov.in/uploads1/candprofile/E27/2024/AC/S13/GOPAL-2024-20241104033952.jpg" alt=""></figure>
                    <div class="cand-info">
                        <div class="status lost">
                            <div style="text-transform: capitalize">lost</div>
                            <div>2396 <span>( -144443)</span></div>
                        </div>
                        <div class="nme-prty">
                            <h5>GOPAL SURESH BHANDARI</h5>
                            <h6>Independent</h6>
                        </div>
                    </div>
                </div>
            </div>
                        <div class="col-md-4 col-12">
                <div class="cand-box">
                    <figure><img src="img/nota.jpg" alt=""></figure>
                    <div class="cand-info">
                        <div class="status ">
                            <div style="text-transform: capitalize"></div>
                            <div>2425 <span>( -144414)</span></div>
                        </div>
                        <div class="nme-prty">
                            <h5>NOTA</h5>
                            <h6>None of the Above</h6>
                        </div>
                    </div>
                </div>
            </div>
                    </div>
    </div>
</div>"""


soup = BeautifulSoup(html_content, "html.parser")

# Container holding the candidate details
candidate_containers = soup.find_all('div', class_='cand-box')

# Extract data for each candidate
results = []
for container in candidate_containers:
    # Extract name and party
    name = container.find('h5').text.strip()
    party = container.find('h6').text.strip()
    
    # Extract votes and status
    status_div = container.find('div', class_='status')
    status = status_div.find('div', style="text-transform: capitalize").text.strip() if status_div else "Unknown"
    votes = status_div.find_all('div')[1].text.strip() if status_div else "0"
    
    results.append({
        'Candidate Name': name,
        'Party': party,
        'Votes': votes.split()[0],  # Extract vote number only
        'Status': status,
        'Vote Margin': votes.split("(")[-1].strip(")")
    })


for result in results:
    print(result)

