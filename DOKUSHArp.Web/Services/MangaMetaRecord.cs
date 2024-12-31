namespace DOKUSHArp.Web.Services;

public sealed record MangaMetaRecord
{
	public required string Id { get; set; }

	public required string Title { get; set; }

	public required int NumCoverPages { get; set; }
}
