namespace DOKUSHArp.Web.Services;

public sealed record MangaReaderMeta
{
	public required string Title { get; set; }

	public required int NumCoverPages { get; set; }

	public int CurrentPage { get; set; }
}