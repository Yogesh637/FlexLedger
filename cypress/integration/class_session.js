describe("FlexLedger — Credit Ledger Lifecycle", () => {
    before(() => {
        cy.login("Administrator");
    });

    it("deducts credits on submission and restores them on cancellation", () => {
        const suffix = Date.now();
        const sessionType = `Cypress Session ${suffix}`;
        const memberName = `Cypress Member ${suffix}`;
        const trainerName = `Cypress Trainer ${suffix}`;
        const initialCredits = 5;
        const creditsRequired = 2;

        let member;
        let trainer;
        let packageName;
        let sessionName;

        // 1. Create Session Type
        cy.request("POST", "/api/resource/Session Type", {
            session_type_name: sessionType,
            credits_required: creditsRequired,
            duration_minutes: 60,
        })
            .then(() => {
                // 2. Create Trainer
                return cy.request("POST", "/api/resource/Trainer", {
                    trainer_name: trainerName,
                    specialization: sessionType,
                    status: "Active",
                });
            })
            .then(() => {
                // 3. Create Member
                return cy.request("POST", "/api/resource/Member", {
                    member_name: memberName,
                    phone: `9${String(suffix).slice(-9)}`,
                    status: "Active",
                });
            })
            .then((response) => {
                member = response.body.data.name;

                // 4. Create Package Purchase
                return cy.request("POST", "/api/resource/Package Purchase", {
                    member,
                    total_credits: initialCredits,
                    credits_used: 0,
                    credits_remaining: initialCredits,
                    amount_paid: 1000,
                    purchase_date: "2026-09-29",
                    expiry_date: "2027-09-29",
                    status: "Active",
                });
            })
            .then((response) => {
                packageName = response.body.data.name;

                // 5. Fetch Trainer name
                return cy.request(
                    "GET",
                    `/api/resource/Trainer?filters=${encodeURIComponent(
                        JSON.stringify([
                            ["trainer_name", "=", trainerName],
                        ])
                    )}&fields=${encodeURIComponent(
                        JSON.stringify(["name"])
                    )}`
                );
            })
            .then((response) => {
                trainer = response.body.data[0].name;

                // 6. Create Class Session
                return cy.request("POST", "/api/resource/Class Session", {
                    session_type: sessionType,
                    trainer,
                    session_date: "2026-09-29",
                    start_time: "10:00:00",
                    status: "Completed",
                    attendees: [
                        {
                            member,
                            package_purchase: packageName,
                            attendance_status: "Attended",
                            credits_charged: creditsRequired,
                        },
                    ],
                });
            })
            .then((response) => {
                sessionName = response.body.data.name;

                // 7. Fetch latest session and submit
                return cy.request(
                    "GET",
                    `/api/resource/Class Session/${sessionName}`
                );
            })
            .then((response) => {
                return cy.request(
                    "POST",
                    "/api/method/frappe.client.submit",
                    {
                        doc: JSON.stringify(response.body.data),
                    }
                );
            })
            .then(() => {
                // 8. Verify credits after submission
                return cy.request(
                    "GET",
                    `/api/resource/Package Purchase/${packageName}`
                );
            })
            .then((response) => {
                expect(response.body.data.credits_remaining).to.equal(3);
                expect(response.body.data.credits_used).to.equal(2);

                // 9. Fetch latest session before cancellation
                return cy.request(
                    "GET",
                    `/api/resource/Class Session/${sessionName}`
                );
            })
            .then(() => {
                // 10. Cancel session with correct arguments
                return cy.request(
                    "POST",
                    "/api/method/frappe.client.cancel",
                    {
                        doctype: "Class Session",
                        name: sessionName,
                    }
                );
            })
            .then(() => {
                // 11. Verify credits were restored
                return cy.request(
                    "GET",
                    `/api/resource/Package Purchase/${packageName}`
                );
            })
            .then((response) => {
                expect(response.body.data.credits_remaining).to.equal(5);
                expect(response.body.data.credits_used).to.equal(0);
            });
    });
});