public class ArrayBounds {
    /*
 * Origin of the benchmark:
 *     repo: https://github.com/diffblue/cbmc.git
 *     branch: develop
 *     directory: regression/cbmc-java/ArrayIndexOutOfBoundsException1
 * The benchmark was taken from the repo: 24 January 2018
 */
    public static void main(String args[]) {
        try {
            int[] a=new int[4];
            a[args.length]=0;
        }
        catch (ArrayIndexOutOfBoundsException exc) {
            assert false;
        }
    }
  
}
