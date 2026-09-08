import type { Metadata } from "next"
import renderPoliticiansDirectory, {
    generateDirectoryMetadata,
    resolveStateBySlug,
} from "@/lib/politicians/directory-page"
import { parsePartyParam } from "@/lib/politicians/directory"

export const dynamic = "force-dynamic"

export async function generateMetadata({
    params,
    searchParams,
}: {
    params: Promise<{ page: string }>
    searchParams: Promise<{ q?: string; party?: string; state?: string }>
}): Promise<Metadata> {
    const { page: pageStr } = await params
    const { q, party, state } = await searchParams
    const page = Math.max(1, parseInt(pageStr, 10) || 1)
    const resolvedState = await resolveStateBySlug(state)
    return generateDirectoryMetadata(page, {
        type: "MLA",
        q,
        parties: parsePartyParam(party),
        ...(resolvedState ?? {}),
    })
}

export default async function PoliticiansMlaPaginatedPage({
    params,
    searchParams,
}: {
    params: Promise<{ page: string }>
    searchParams: Promise<{ q?: string; party?: string; state?: string }>
}) {
    const { page: pageStr } = await params
    const { q, party, state } = await searchParams
    const page = Math.max(1, parseInt(pageStr, 10) || 1)
    const resolvedState = await resolveStateBySlug(state)
    return renderPoliticiansDirectory({
        page,
        filters: {
            type: "MLA",
            q,
            parties: parsePartyParam(party),
            ...(resolvedState ?? {}),
        },
    })
}
