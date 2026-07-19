import { expect, test } from "@playwright/test";

function createPdf(text: string): Buffer {
  const escaped = text.replace(/([\\()])/g, "\\$1");
  const stream = `BT /F1 11 Tf 72 720 Td (${escaped}) Tj ET`;
  const objects = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
    `<< /Length ${Buffer.byteLength(stream)} >>\nstream\n${stream}\nendstream`,
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
  ];
  let pdf = "%PDF-1.4\n";
  const offsets = [0];
  objects.forEach((object, index) => {
    offsets.push(Buffer.byteLength(pdf));
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });
  const xrefOffset = Buffer.byteLength(pdf);
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  pdf += offsets.slice(1).map((offset) => `${String(offset).padStart(10, "0")} 00000 n \n`).join("");
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`;
  return Buffer.from(pdf);
}

test("candidate uploads a resume, matches a job, reviews materials, and confirms the application", async ({ page }) => {
  await page.goto("/");

  await page.getByTitle("Resume").click();
  await page.getByTestId("resume-file").setInputFiles({
    name: "taylor-resume.pdf",
    mimeType: "application/pdf",
    buffer: createPdf("Python FastAPI React PostgreSQL Docker RAG ChromaDB backend engineer"),
  });
  await page.getByTestId("upload-resume").click();
  await expect(page.getByText(/Uploaded taylor-resume\.pdf/)).toBeVisible();

  await page.getByTitle("Jobs").click();
  await page.getByTestId("job-company").fill("Example Labs");
  await page.getByTestId("job-title").fill("Backend Engineer");
  await page.getByTestId("job-location").fill("London");
  await page.getByTestId("job-url").fill("https://example.com/jobs/backend-engineer");
  await page.getByTestId("job-description").fill(
    "We require Python, FastAPI, React, PostgreSQL, Docker, RAG, and ChromaDB skills to build reliable APIs.",
  );
  await page.getByTestId("import-job").click();
  await expect(page.getByText("Imported job: Example Labs - Backend Engineer")).toBeVisible();

  await page.getByTestId("match-job").click();
  await expect(page.getByText(/Score: \d+\/100\. Application:/)).toBeVisible();

  await page.getByTitle("Pending").click();
  await page.getByTestId("pending-application").click();
  await expect(page.getByRole("heading", { name: "Example Labs · Backend Engineer" })).toBeVisible();

  await page.getByTestId("cover-letter").fill("Reviewed and tailored cover letter for Example Labs.");
  await page.getByTestId("save-cover-letter").click();
  await page.getByTestId("confirm-application").click();
  await expect(page.getByText("No jobs are waiting for confirmation.")).toBeVisible();
});
